from flask import render_template, flash, redirect, url_for, session, request
from app import app
from app.forms import URLForm
import spotipy
import spotipy.util as util
import os
import time
import json
from bot import generate_playlist

API_BASE = 'https://accounts.spotify.com'

# Make sure you add this to Redirect URIs in the setting of the application dashboard
REDIRECT_URI = "http://127.0.0.1:5000/api_callback"

SCOPE = 'playlist-modify-private'
SHOW_DIALOG = True

client_id = os.environ['SPOTIPY_CLIENT_ID']
client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
redirect_uri = os.environ['SPOTIPY_REDIRECT_URI']

# authorization-code-flow Step 1. Have your application request authorization; 
# the user logs in and authorizes access
@app.route("/", methods=['GET', 'POST'])
@app.route("/index", methods=['GET', 'POST'])
def index():
    form = URLForm()
    if form.validate_on_submit():
        flash('Playlist requested for URL {}'.format(form.url.data))
        session['reddit_url'] = form.url.data
        sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = client_id, client_secret = client_secret, redirect_uri = redirect_uri, scope = SCOPE)
        auth_url = sp_oauth.get_authorize_url()
        print(auth_url)
        return redirect(auth_url)

    if 'result' in session:
        return render_template('base.html', form=form, result=session.pop('result', None))
    else:
        return render_template('base.html', form=form)
    

# authorization-code-flow Step 2.
# Have your application request refresh and access tokens;
# Spotify returns access and refresh tokens
@app.route("/api_callback")
def api_callback():
    # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = client_id, client_secret = client_secret, redirect_uri = redirect_uri, scope = SCOPE)
    # Save reddit url
    reddit_url = session.get('reddit_url')

    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)

    # Saving the access token along with all other token related info
    session["token_info"] = token_info
    session['reddit_url'] = reddit_url

    authorized = get_token(session)
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    success = generate_playlist(session.get('reddit_url'), sp)
    result = {'success': success}
    session.clear()
    session['result'] = result

    return redirect('index')

# Checks to see if token is valid and gets a new token if not
def get_token(session):
    token_valid = False
    token_info = session.get("token_info", {})

    # Checking if the session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    # Refreshing token if it has expired
    if (is_token_expired):
        # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
        sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = client_id, client_secret = client_secret, redirect_uri = REDIRECT_URI, scope = SCOPE)
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid

if __name__ == "__main__":
    app.run(debug=True)
