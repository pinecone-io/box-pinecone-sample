from box_integration import box_client
from pinecone_integration import pinecone_client

def main():
    # Initialize Box client
    box = box_client.initialize()
    
    # Initialize Pinecone client
    pinecone = pinecone_client.initialize()
    
    # Example: Upload a file to Box and store metadata in Pinecone
    file_id = box.upload_file("path/to/file.txt")
    pinecone.store_metadata(file_id, {"description": "Sample file uploaded to Box"})
    
    print("Integration complete!")

if __name__ == "__main__":
    main()
