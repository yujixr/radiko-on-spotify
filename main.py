import config
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


def check(station: str, playlist: str, access_token: str):
    radiko_xml = radiko.fetch(station)

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

    spotify.delete_music_from_playlist(playlist, spotify_ids, access_token)
    spotify.add_music_to_playlist(playlist, spotify_ids, access_token)


access_token = spotify.auth(
    config.refresh_token,
    config.client_token,
    config.client_secret
)

check("TBS", "11OVi6X97j56J64adgdF5o", access_token)
check("QRR", "304jv8dR1DnFveTH969ObD", access_token)
check("RN2", "0MZ068JyJDhdOGDoAc1LML", access_token)
check("INT", "6ql2qiuO69kjTZK8FZzDyJ", access_token)
check("FMT", "0hzw8H4PSmFDd0K952AjT7", access_token)
check("FMJ", "2dK6F6vzYm9yfPI7MCkAb7", access_token)
check("BAYFM78", "0AzldR8iNos8ZpUDc6uQUu", access_token)
check("NACK5", "4bznTT4izxtHxWJNnEo6lL", access_token)
check("YFM", "0YEpGbfFBxo04HGIQzldMM", access_token)
