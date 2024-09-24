import config
import openai
from pinecone_integration.query_utils import initialize_pinecone_client, vectorize_query, query_pinecone


def initialize_openai():
    openai.api_key = config.OPENAI_API_KEY

def query_openai_for_answer(query_text, context):
    response = openai.ChatCompletion.create(
        model="gpt-4",  # or "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Only use the provided context to answer the question."},
            {"role": "user", "content": f"Context: {context}"},
            {"role": "user", "content": f"Question: {query_text}. Please only use the above context to answer."},
        ],
        max_tokens=150
    )
    return response['choices'][0]['message']['content'].strip()

def main():
    # Initialize OpenAI and Pinecone clients
    initialize_openai()
    pinecone_client = initialize_pinecone_client()
    
    # Get user input for the question
    query_text = input("Enter your question: ")
    
    # Vectorize the query
    query_vector = vectorize_query(pinecone_client, query_text)
    
    # Query Pinecone and retrieve top 5 results
    results = query_pinecone(pinecone_client, query_vector, top_k=5)
    
    # Combine all the relevant chunk texts from the top results
    combined_text = " ".join([match['metadata']['chunk_text'] for match in results['matches']])
    
    # Use OpenAI to extract the answer
    answer = query_openai_for_answer(query_text, combined_text)
    
    print(f"Answer: {answer}")

if __name__ == "__main__":
    main()





