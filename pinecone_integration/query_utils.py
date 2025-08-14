import config
from pinecone import Pinecone
import logging

logging.getLogger("pinecone")

def initialize_pinecone_client():
    pinecone = Pinecone(
        api_key=config.PINECONE_API_KEY, 
        source_tag="box_pinecone_integration"
    )
    return pinecone

# Commenting out as it's not needed for the query_pinecone function
#def vectorize_query(client, query_text):
#    # Vectorize the query text using Pinecone inference API
#    query_embedding = client.inference.embed(
#        model="multilingual-e5-large",
#        inputs=[query_text],
#        parameters={
#            "input_type": "passage",
#            "truncate": "END"
#        }
#    )
#   # Extract the embedding values (list of floats)
#    return query_embedding[0]['values']

def query_pinecone(index, query_text, box_user_id, top_k=50):
    """
    Queries the Pinecone index with the given query text and retrieves the top_k results.

    Parameters:
    - index: The Pinecone index to search in.
    - query_text: The text of the query to search for in the index.
    - box_user_id: The namespace identifier for the Box user, used to scope the search.
    - top_k: The number of top results to retrieve from the index (default is 50).

    Returns:
    - A list of query results from the Pinecone index, including the top_k results based on the query text.
    """
    logging.info(f"Querying Pinecone with query: {query_text}")
    query_results = index.search(
        namespace=box_user_id,
        query={
            "inputs": {"text": query_text},
            "top_k": top_k,
        },
        fields=["chunk_text"],
        rerank={
            "model": "cohere-rerank-3.5",
            "top_n": int(top_k/2),
            "rank_fields": ["chunk_text"]
        }
    )
    
    return query_results
