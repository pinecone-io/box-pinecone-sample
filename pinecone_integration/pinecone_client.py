import pinecone

def initialize():
    # Replace with your actual API key
    pinecone.init(api_key='YOUR_PINECONE_API_KEY')
    return pinecone

def store_metadata(file_id, metadata):
    index = pinecone.Index('your-index-name')
    index.upsert(items=[(file_id, metadata)])
