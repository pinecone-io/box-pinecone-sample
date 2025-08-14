import config
from openai import OpenAI
from box_integration.box_client import get_client
from datetime import datetime
from pinecone_integration.query_utils import query_pinecone
from pinecone_integration.pinecone_client import get_pinecone_index


def initialize_openai():
    """
    Initializes and returns an OpenAI client using the API key from the configuration.

    Returns:
    - An OpenAI client instance.
    """
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    return client

def query_openai_for_answer(openai_client, query_text, context):
    """
    Queries OpenAI's API to generate an answer based on the provided query text and context.

    Parameters:
    - openai_client: The OpenAI client used to interact with the OpenAI service.
    - query_text: The question or query to be answered.
    - context: The context or background information to be used for generating the answer.

    Returns:
    - The generated answer as a string.
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    messages=[
        {"role": "system", "content": f"""
        You are a helpful assistant. 
        Use the provided context to answer the question. Focus on answering the question based on the context provided.
        Consider synonymous or related terms when identifying entities. 
        The current date is {current_date}.
        The user is requesting information about the context provided.
        Keep your answer concise and to the point.
        Keep your tone professional and avoid using emojis.
        Make sure to answer the question in a friendly and engaging tone.
        """,
        },
        {"role": "user", "content": f"Context: {context}\n"},
        {"role": "user", "content": f"""
        Question: {query_text}. 
        Please use the above context to answer, considering synonymous or related terms and the temporal context.
        Focus on answering the question based on the context provided.
        Keep your answer concise and to the point.
        Keep your tone professional and avoid using emojis.
        Make sure to answer the question in a friendly and engaging tone.
        """,
        },
    ]
    response = openai_client.chat.completions.create(model="gpt-4", messages=messages, max_tokens=150)
    return response.choices[0].message.content.strip()

def main():
    """
    Main function to interactively query OpenAI and Pinecone for answers based on user input.
    """
    # Initialize OpenAI and Pinecone clients
    openai_client = initialize_openai()
    pinecone_index = get_pinecone_index()

    # Initialize Box client
    box_client = get_client()

    # Get Box User ID for namespacing
    box_user = box_client.user().get()

    while True:
        try:
            # Get user input for the question
            query_text = input("Enter your question (or 'q' to quit): ")
            if query_text.lower() == 'q':
                break

            # Vectorize the query
            #query_vector = vectorize_query(pinecone_index, query_text)

            # Query Pinecone and retrieve top 5 results
            results = query_pinecone(pinecone_index, query_text, box_user.id, top_k=5)

            # Combine all the relevant chunk texts from the top results
            combined_text = " ".join(hit['fields']['chunk_text'] for hit in results['result']['hits'])

            # Use OpenAI to extract the answer
            answer = query_openai_for_answer(openai_client, query_text, combined_text)

            print(f"Answer: {answer}")
        except EOFError:
            print("Exiting...")
            break

if __name__ == "__main__":
    main()





