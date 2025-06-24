import asyncio
import os

from pinecone import Pinecone
from pinecone_plugins.assistant.models.chat import Message

from box_integration.box_client import get_client
from box_integration.box_integration import download_files, get_files_in_folder

import config

PINECONE_API_KEY = config.PINECONE_API_KEY

async def main():
    
    if not PINECONE_API_KEY:
        print("Error: PINECONE_API_KEY environment variable not set.")
        return
    
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # Initialize Box client
    box_client = get_client()

    # Get Box User ID for namespacing
    box_user = box_client.user().get()

    # Define the Box folder ID containing the files
    folder_id = config.BOX_FOLDER_ID
    
    # Get all files in the specified folder
    files = get_files_in_folder(box_client, folder_id)

    download_files(box_client, files)

    assistant = pc.assistant.create_assistant(
        assistant_name="box-assistant", 
        instructions="Use American English for spelling and grammar.", # Description or directive for the assistant to apply to all responses.
        region="us", # Region to deploy assistant. Options: "us" (default) or "eu".
        timeout=30 # Maximum seconds to wait for assistant status to become "Ready" before timing out.
    )

    # Define the Box folder ID containing the files
    folder_id = config.BOX_FOLDER_ID
    
    # Get all files in the specified folder
    files = get_files_in_folder(box_client, folder_id)

    print("Downloading files...")

    file_names = download_files(box_client, files)

    print("Uploading files...")

    for file_name in file_names:
        # Upload a file.
        response = assistant.upload_file(
            file_path=f"./{file_name}",
            metadata={"box_user_id": box_user.id},
            timeout=None
        )
    
    while True:
        try:
            user_input = await asyncio.to_thread(input, "You: ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if user_input.lower() in ["quit", "exit"]:
            print("Exiting...")
            break
        
        if not user_input.strip():
            continue

        msg = Message(role="user", content=user_input)
        resp = assistant.chat(messages=[msg])

        print(f"Assistant:\n{resp.message.content}")

    pc.assistant.delete_assistant(
        assistant_name="box-assistant", 
    )

if __name__ == "__main__":
    asyncio.run(main())