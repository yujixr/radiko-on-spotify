import sys

import pandas as pd
import requests

import itunes
import radiko
import spotify


def get_spotify_id(track_data, access_token: str):
    if track_data is None:
        return None

    artist_name, album_name, track_name = track_data
    music_id = spotify.search(artist_name, album_name,
                              track_name, "JP", access_token)
    if music_id is not None:
        return music_id

    return spotify.search(artist_name, album_name,
                          track_name, "SG", access_token)


def get_track_data_from_itunes(itunes_id: str, country: str):
    if itunes_id is None:
        return None

    return itunes.get_detail(itunes_id, country)


def check(station: str, playlist_id: str, access_token: str):
    radiko_xml = radiko.fetch(station)

    name = radiko.get_station_name(radiko_xml)
    description = name + "で流された楽曲を自動検出し、プレイリストに追加しています。（Spotifyにない楽曲などは追加されません）"
    spotify.change_a_playlists_details(
        playlist_id, name, description, access_token)

    try:
        spotify_ids = pd.read_csv("./musics/"+station+".txt", header=None).values.reshape(1, -1).tolist()[0]
    except:
        spotify_ids = []

    for item in radiko_xml[1].iter('item'):
        itunes_id = radiko.extract_itunes_id(item)

        track_data = get_track_data_from_itunes(itunes_id, "JP")
        spotify_id = get_spotify_id(track_data, access_token)

        if spotify_id is None:
            track_data = get_track_data_from_itunes(itunes_id, "US")
            spotify_id = get_spotify_id(track_data, access_token)

        if spotify_id is None:
            track_data = radiko.get_detail(item)
            spotify_id = get_spotify_id(track_data, access_token)

        if spotify_id is not None:
            spotify_ids.append(spotify_id)
        print(radiko.get_detail(item), spotify_id)

    spotify_ids = pd.DataFrame(spotify_ids)
    spotify_ids.drop_duplicates(keep="last", inplace=True)
    spotify_ids.to_csv("./musics/"+station+".txt", header=False, index=False)

    spotify.replace_a_playlists_items(
        playlist_id,
        spotify_ids[-100::].values.reshape(1, -1).tolist()[0],
        access_token
    )


refresh_token = sys.argv[1]
client_token = sys.argv[2]
client_secret = sys.argv[3]
station = sys.argv[4]
playlist_id = sys.argv[5]
access_token = spotify.auth(
    refresh_token,
    client_token,
    client_secret
)

check(station, playlist_id, access_token)
