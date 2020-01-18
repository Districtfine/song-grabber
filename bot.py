import praw
import re
import spotipy
import spotipy.util as util
import os
import sys

def generate_playlist(threadInput, sp):
    try:
        reddit = praw.Reddit(client_id=os.getenv('PRAW_CLIENT_ID'),
                             client_secret=os.getenv('PRAW_CLIENT_SECRET'),
                             user_agent=os.getenv('PRAW_USER_AGENT'))
    except Exception as e:
        print(e)
        return (False, "Could not initialize reddit bot, please try again")

    redditLinkRegex = re.compile(r"redd(?:it\.com|\.it).*(?:\/comments)?(\/\w{2,7}\b)(\/.*)?", re.IGNORECASE)
    redditLinkMatch = redditLinkRegex.search(threadInput)
    if redditLinkMatch:
        try:
            submission = reddit.submission(id=redditLinkMatch.group(1)[1:])
        except:
            return (False, "Could not retrieve comment thread, please try again") 
    else:
        return (False, "Inputed string was not a valid reddit thread")

    # Expand out submission commment forest TODO: Find out whether a limit of 1 is acceptable
    while True:
        try:
            submission.comments.replace_more(limit=1)
            break
        except:
            continue

    songURIs = []
    for comment in submission.comments.list():
        if "open.spotify.com/track/" in comment.body:
            spotifyLinkRegex = re.compile(r"https?://open.spotify.com/track/[^ \)]+", re.IGNORECASE)
            songLinkMatch = spotifyLinkRegex.search(comment.body)
            if songLinkMatch:
                fullLink = songLinkMatch.group()
                # Extract just the track id before appending into list
                URIRegex = re.compile(r"track/([a-zA-Z0-9]*)(\?|$)")
                songURIMatch = URIRegex.search(fullLink)
                if songURIMatch:
                    songURIs.append(songURIMatch.group(1))
                # Something has gone horribly wrong, all song links should have URIs
                else: 
                    return (False, "Problem encountered while searching comment thread")
                    
    # Remove duplicates from song list
    songURIs = list(dict.fromkeys(songURIs))

    playlistName = redditLinkMatch.group(0)[:99]
    sp.trace = False
    try:
        playlist = sp.user_playlist_create(sp.me()['id'], playlistName, False)
    except:
        return (False, "Problem encounted while creating playlist, please try again")
    try:
        sp.user_playlist_add_tracks(sp.me()['id'], playlist['id'], songURIs[0:9999])
    except:
        return (False, "Problem encountered while adding tracks to playlist, please try again")
    return (True, "Success")
