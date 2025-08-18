from flask import Flask, render_template, request, jsonify, redirect
from pinecone_integration.pinecone_client import get_pinecone_index
from pinecone_integration.query_utils import query_pinecone
from box_integration.box_oauth import oauth_from_previous
from box_integration.box_integration import get_user_id
from box_integration.box_client import Client
import web_config as config
import logging
from query import initialize_openai, query_openai_for_answer

app = Flask(__name__)

@app.route('/')
def index():
    oauth = oauth_from_previous()
    if not oauth.access_token:
        auth_url, csrf_token = oauth.get_authorization_url(config.REDIRECT_URI)
        return redirect(auth_url)
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def get_context_and_query():
    oauth = oauth_from_previous()
    client = Client(oauth)
    default_context = """
    You need to return the answer in markdown format.
    You need to format the answer in an easy to read and follow manner, including bullet points, lists, and other formatting. 
    If a sentence is too long, break it up into multiple sentences.
    You need to return the answer in a friendly and engaging tone.
    """
    namespace = get_user_id(client)
    user_query = request.json.get('query')
    index = get_pinecone_index()
    search_results = query_pinecone(index, user_query, namespace, top_k=10)
    context = [hit['fields']['chunk_text'] for hit in search_results['result']['hits']]
    combined_context = " ".join(default_context) + "\n\n" + " ".join(context)
    openai_client = initialize_openai()
    bare_context = query_openai_for_answer(openai_client, user_query, default_context)
    contextual_context = query_openai_for_answer(openai_client, user_query, combined_context)
    return jsonify({'contextual_response': contextual_context, 'bare_response': bare_context})

@app.route('/login')
def login():
    oauth = oauth_from_previous()
    auth_url, csrf_token = oauth.get_authorization_url(config.REDIRECT_URI)
    return redirect(auth_url)

@app.route('/callback')
def callback():
    oauth = oauth_from_previous()
    code = request.args.get('code')
    try:
        oauth.authenticate(code)
        return redirect('/')
    except Exception as e:
        logging.error(f'Error during authentication: {e}')
        return 'Authentication failed', 500

if __name__ == '__main__':
    app.run(debug=True)
