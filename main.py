"""main.py"""

from box_integration.box_integration import get_files_in_folder, get_file_text_content
from pinecone_integration.pinecone_client import initialize_pinecone_client, store_metadata_in_pinecone
import config
import logging
from box_integration.box_client import get_client

logging.basicConfig(level=logging.INFO)
logging.getLogger("boxsdk").setLevel(logging.CRITICAL)

def main():
    # Initialize Box client
    box_client = get_client()

    # Get Box User ID for namespacing
    box_user = box_client.user().get()
    
    # Initialize Pinecone client
    pinecone_client = initialize_pinecone_client()
    
    # Define the Box folder ID containing the files
    folder_id = config.BOX_FOLDER_ID
    
    # Get all files in the specified folder
    files = get_files_in_folder(box_client, folder_id)
    
    # Process each file
    for file in files:
        try:
            # Extract text content from the file representation
            text_content = get_file_text_content(box_client, file)
            
            # Extract metadata from the file object
            metadata = {
                "file_name": file.name,
                "file_id": file.id,
                "created_at": file.created_at,
                "modified_at": file.modified_at,
                "size": file.size,
                "box_user_id": box_user.id
            }
            
            # Combine text content with metadata for vectorization
            combined_text = text_content + " " + " ".join(f"{key}: {value}" for key, value in metadata.items())
            # print((f"Text: {combined_text}"))
            # Store the vectorized representation and metadata in Pinecone
            store_metadata_in_pinecone(pinecone_client, file.id, {"text": combined_text, **metadata}, box_user.id)
            
            print(f"Processed and stored metadata for file: {file.name}")
        
        except Exception as e:
            print(f"Failed to process file {file.name}: {e}")
    
    print("Processed and stored metadata for all files in the folder.")

if __name__ == "__main__":
    main()
