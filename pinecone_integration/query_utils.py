import config
from pinecone import Pinecone

def initialize_pinecone_client():
    pinecone = Pinecone(
        api_key=config.PINECONE_API_KEY
    )
    return pinecone

def vectorize_query(client, query_text):
    # Vectorize the query text using Pinecone inference API
    query_embedding = client.inference.embed(
        model="multilingual-e5-large",
        inputs=[query_text],
        parameters={
            "input_type": "passage",
            "truncate": "END"
        }
    )
    # Extract the embedding values (list of floats)
    return query_embedding[0]['values']

def query_pinecone(client, query_vector, top_k=5):
    index_name = config.PINECONE_INDEX
    index = client.Index(index_name)
    
    # Query the index with the vector and return top_k results
    query_results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )
    
    return query_results
