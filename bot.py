import praw
import re
import spotipy
import spotipy.util as util
import os
import sys

def generate_playlist(threadInput, sp):
    reddit = praw.Reddit('readBot')

    submission = reddit.submission(url=threadInput)

    songURIs = []

    while True:
        try:
            submission.comments.replace_more()
            break
        except:
            continue

    for comment in submission.comments.list():
        if "open.spotify.com/track/" in comment.body:
            spotifyLinkRegex = re.compile(r"https?://open.spotify.com/track/[^ \)]+", re.IGNORECASE)
            songLinkMatch = spotifyLinkRegex.search(comment.body)
            if songLinkMatch:
                fullLink = songLinkMatch.group()
                # Extract just the track id before appending into list
                URIRegex = re.compile(r"/[a-zA-Z0-9]*\?")
                songURIMatch = URIRegex.search(fullLink)
                if songURIMatch:
                    songURIs.append(songURIMatch.group()[1:-1]) # Strip out first '/' and last '?'
                # Something has gone horribly wrong, all song links should have URIs
                else: 
                    # TODO: Do some proper error handling here
                    return False
                    

    playlistName = threadInput
    sp.trace = False
    playlist = sp.user_playlist_create(sp.me()['id'], playlistName, False)
    sp.user_playlist_add_tracks(sp.me()['id'], playlist['id'], songURIs)
    return True
