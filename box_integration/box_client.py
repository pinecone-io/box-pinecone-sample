"""
Handles the box client object creation.
Orchestrates the authentication process.
"""

from boxsdk import Client
from box_integration.box_oauth import oauth_from_previous
from box_integration.oauth_callback import callback_handle_request, open_browser
import config


def get_client() -> Client:
    """
    Returns a boxsdk Client object.
    """
    oauth = oauth_from_previous()

    if not oauth.access_token:
        auth_url, csrf_token = oauth.get_authorization_url(config.REDIRECT_URI)
        open_browser(auth_url)
        callback_handle_request(csrf_token)

    oauth = oauth_from_previous()

    if not oauth.access_token:
        raise RuntimeError("Unable to authenticate")

    oauth.refresh(oauth.access_token)

    return Client(oauth)
