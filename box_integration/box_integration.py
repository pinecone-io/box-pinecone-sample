import requests
import config
import re

# Supported file types for text representation
SUPPORTED_TEXT_FILE_TYPES = {
    ".doc", ".docx", ".pdf", ".txt", ".html", ".md", ".json", ".xml",
    ".ppt", ".pptx", ".key",
    ".xls", ".xlsx", ".csv"
}

def is_supported_file_type(file_name):
    # Check if the file's extension is in the supported list
    return any(file_name.endswith(ext) for ext in SUPPORTED_TEXT_FILE_TYPES)

def get_files_in_folder(client, folder_id):
    client.user().get(headers={"x-box-ai-library": "pinecone"})
    folder = client.folder(folder_id).get()
    items = folder.get_items()
    file_objects = []
    for item in items:
        if item.type == 'file' and is_supported_file_type(item.name):
            file_objects.append(item.get())
    return file_objects

def clean_up_text(content: str) -> str:
    # Fix hyphenated words broken by newline
    content = re.sub(r'(\w+)-\n(\w+)', r'\1\2', content)

    # Remove specific unwanted patterns and characters
    unwanted_patterns = [
        "\\n", "  —", "——————————", "—————————", "—————",
        r'\\u[\dA-Fa-f]{4}', r'\uf075', r'\uf0b7'
    ]
    for pattern in unwanted_patterns:
        content = re.sub(pattern, "", content)

    # Fix improperly spaced hyphenated words and normalize whitespace
    content = re.sub(r'(\w)\s*-\s*(\w)', r'\1-\2', content)
    content = re.sub(r'\s+', ' ', content)

    return content

def get_file_text_content(client, file):
    rep_hints = '[extracted_text]'
    oauth2 = client.auth  # Access the OAuth2 object from the client
    access_token = oauth2.access_token  # Retrieve the current access token
    representations = client.file(file.id).get_representation_info(rep_hints)
    # Check if the representation is ready to download
    for representation in representations:
        if not representation['status']['state'] == 'success':
            raise ValueError(f"Representation not ready: {representation['status']['state']}")
        # # Get the URL for the representation
        download_url = representation['content']['url_template'].replace('{+asset_path}', '') + '?access_token=' + access_token
        print(download_url)
        # # Use the URL to download the text content
        response = requests.get(download_url)
        response.raise_for_status()  # Ensure we raise an error for bad status codes
        cleaned_text = clean_up_text(response.text)
        
        return cleaned_text

