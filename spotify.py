import base64
import json

import requests


def auth(refresh_token: str, client_token: str, client_secret: str):
    res = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        },
        headers={
            "Authorization": "Basic " + base64.b64encode((client_token+":"+client_secret).encode()).decode()
        }
    ).text
    res_json = json.loads(res)
    return res_json["access_token"]


def search(artist_name: str, album_name: str, track_name: str, country: str, access_token: str):
    res = requests.get(
        "https://api.spotify.com/v1/search",
        params={
            "q": artist_name + " " + album_name + " " + track_name,
            "type": "track",
            "market": country
        },
        headers={'Authorization': 'Bearer ' + access_token}
    ).text

    res_json = json.loads(res)
    if "tracks" not in res_json or res_json["tracks"]["total"] == 0:
        return None

    return res_json["tracks"]["items"][0]["id"]


def delete_music_from_playlist(playlist_id: str, music_ids: [str], access_token: str):
    query = []
    for music_id in music_ids:
        query.append({
            "uri": "spotify:track:" + music_id
        })

    requests.delete(
        "https://api.spotify.com/v1/playlists/" + playlist_id + "/tracks",
        json={"tracks": query},
        headers={
            'Authorization': 'Bearer ' + access_token,
            "Content-Type": "application/json"
        }
    )


def add_music_to_playlist(playlist_id: str, music_ids: [str], access_token: str):
    query = []
    for music_id in music_ids:
        query.append({
            "uri": "spotify:track:" + music_id
        })

    requests.post(
        "https://api.spotify.com/v1/playlists/" + playlist_id + "/tracks",
        json={
            "uris": query,
            "position": 0
        },
        headers={
            'Authorization': 'Bearer ' + access_token,
            "Content-Type": "application/json"
        }
    )
