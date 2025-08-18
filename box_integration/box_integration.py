import requests
import config
import re
import logging

# Configure logging
log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.ERROR)
logging.basicConfig(level=log_level)
logging.getLogger("box-pinecone-integration")

# Supported file types for text representation
SUPPORTED_TEXT_FILE_TYPES = {
    ".doc", ".docx", ".pdf", ".txt", ".html", ".md", ".json", ".xml",
    ".ppt", ".pptx", ".key",
    ".xls", ".xlsx", ".csv"
}

def is_supported_file_type(file_name):
    """
    Checks if the file's extension is in the supported list.

    Parameters:
    - file_name: The name of the file to check.

    Returns:
    - True if the file's extension is in the supported list, False otherwise.
    """
    logging.debug('Checking if file type is supported for: %s', file_name)
    return any(file_name.endswith(ext) for ext in SUPPORTED_TEXT_FILE_TYPES)

def get_files_in_folder(client, folder_id):
    """
    Fetches all files in the specified folder.

    Parameters:
    - client: The Box client used to interact with the Box service.
    - folder_id: The ID of the folder to fetch files from.

    Returns:
    - A list of file objects.
    """
    logging.debug('Fetching files in folder with ID: %s', folder_id)
    client.user().get(headers={"x-box-ai-library": "pinecone"})
    folder = client.folder(folder_id).get()
    items = folder.get_items()
    file_objects = []
    for item in items:
        if item.type == 'file' and is_supported_file_type(item.name):
            file_objects.append(item.get())
    return file_objects

def clean_up_text(content: str) -> str:
    """
    Cleans up the text content by fixing hyphenated words broken by newline and removing unwanted patterns and characters.

    Parameters:
    - content: The text content to clean up.

    Returns:
    - The cleaned up text content.
    """
    logging.debug('Cleaning up text content')
    if not content:
        logging.warning('No content to clean')
        return content
    
    try:
        content = re.sub(r'(\w+)-\n(\w+)', r'\1\2', content)
    except Exception as e:
        logging.error('Error cleaning up text content: %s', e)
        return content

    unwanted_patterns = [
        "\\n", "  —", "——————————", "—————————", "—————",
        r'\\u[\dA-Fa-f]{4}', r'\uf075', r'\uf0b7'
    ]
    logging.debug('Removing unwanted patterns from text content')
    for pattern in unwanted_patterns:
        content = re.sub(pattern, "", content)

    logging.debug('Fixing improperly spaced hyphenated words and normalizing whitespace')
    content = re.sub(r'(\w)\s*-\s*(\w)', r'\1-\2', content)
    content = re.sub(r'\s+', ' ', content)

    return content

def get_file_text_content(client, file):
    """
    Gets the text content for a file.

    Parameters:
    - client: The Box client used to interact with the Box service.
    - file: The file object to get the text content for.

    Returns:
    - The text content for the file.
    """
    logging.debug('Getting text content for file ID: %s', file.id)
    rep_hints = '[extracted_text]'
    oauth2 = client.auth
    access_token = oauth2.access_token
    representations = client.file(file.id).get_representation_info(rep_hints)
    for representation in representations:
        if not representation['status']['state'] == 'success':
            raise ValueError(f"Representation not ready: {representation['status']['state']}")
        download_url = representation['content']['url_template'].replace('{+asset_path}', '') + '?access_token=' + access_token
        print(download_url)
        response = requests.get(download_url)
        response.raise_for_status()
        cleaned_text = clean_up_text(response.text)
        logging.debug('Cleaned up text content: %s', cleaned_text)
        return cleaned_text

def download_files(client, files):
    """
    Downloads the specified files.

    Parameters:
    - client: The Box client used to interact with the Box service.
    - files: The list of file objects to download.

    Returns:
    - A list of file names.
    """
    logging.debug('Downloading files')
    file_names = []

    for file in files:
        file_name=file.name
        logging.debug('Downloading file: %s', file_name)

        with open(f"./{file_name}", 'wb') as output_file:
            client.file(file.id).download_to(output_file)

        file_names.append(file_name)        

    return file_names

def get_user_id(client):
    """
    Retrieves the Box user ID for the authenticated user.

    Parameters:
    - client: The Box client used to interact with the Box service.

    Returns:
    - The user ID of the authenticated user.
    """
    logging.debug('Retrieving user ID')
    user_info = client.user().get()
    user_id = user_info.id
    logging.info(f'User ID retrieved: {user_id}')
    return user_id