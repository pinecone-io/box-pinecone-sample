from boxsdk import Client, OAuth2

def initialize():
    # Replace with your actual credentials
    oauth2 = OAuth2(
        client_id='YOUR_CLIENT_ID',
        client_secret='YOUR_CLIENT_SECRET',
        access_token='YOUR_ACCESS_TOKEN',
    )
    client = Client(oauth2)
    return client

def upload_file(client, file_path):
    folder_id = '0'  # '0' is the root folder
    with open(file_path, 'rb') as file_stream:
        uploaded_file = client.folder(folder_id).upload_stream(file_stream, file_path)
    return uploaded_file.id
