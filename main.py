from xml.etree import ElementTree
from urllib import parse
import requests
import json
import re
import base64
import config

access_token = ""

def delete_brackets(s):
    """
    括弧と括弧内文字列を削除
    """
    """ brackets to zenkaku """
    table = {
        "(": "（",
        ")": "）",
        "<": "＜",
        ">": "＞",
        "{": "｛",
        "}": "｝",
        "[": "［",
        "]": "］"
    }
    for key in table.keys():
        s = s.replace(key, table[key])
    """ delete zenkaku_brackets """
    l = ['（[^（|^）]*）', '【[^【|^】]*】', '＜[^＜|^＞]*＞', '［[^［|^］]*］',
         '「[^「|^」]*」', '｛[^｛|^｝]*｝', '〔[^〔|^〕]*〕', '〈[^〈|^〉]*〉']
    for l_ in l:
        s = re.sub(l_, "", s)
    """ recursive processing """
    return delete_brackets(s) if sum([1 if re.search(l_, s) else 0 for l_ in l]) > 0 else s

def format(s):
    return delete_brackets(s).strip().replace('\u3000', ' ').translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))

def getTrackData(itunes_id, country):
    itunes_json = json.loads(
        requests.get(
            "http://ax.itunes.apple.com/WebObjects/MZStoreServices.woa/wa/wsLookup",
            params = {
                "id" : itunes_id,
                "country" : country
            }
            ).text
    )
    if itunes_json["resultCount"] is 0:
        return None
    else:
        itunes_json = itunes_json["results"][0]
        return(
            format(itunes_json["artistName"]), 
            format(itunes_json["collectionCensoredName"]), 
            format(itunes_json["trackCensoredName"])
        )

def getTrackData_radiko(radiko_item):
    return (format(radiko_item.attrib['artist']), "", format(radiko_item.attrib['title']))

def getSpotifyId(track_data):
    artist_name,album_name,track_name = track_data
    spotify_json = json.loads(
        requests.get(
            "https://api.spotify.com/v1/search", 
            params = {
                "q" : artist_name + " " + album_name + " " + track_name,
                "type" : "track",
                "market" : "JP"
            },
            headers = { 'Authorization': 'Bearer ' + access_token }
            ).text
        )["tracks"]
    if spotify_json["total"] is 0:
        spotify_json = json.loads(
            requests.get(
                "https://api.spotify.com/v1/search", 
                params = {
                    "q" : artist_name + " " + album_name + " " + track_name,
                    "type" : "track",
                    "market" : "SG"
                },
                headers = { 'Authorization': 'Bearer ' + access_token }
                ).text
            )["tracks"]
        if spotify_json["total"] is 0:
            return None

    return spotify_json["items"][0]["id"]

def getSpotifyId_itunes(itunes_id, country):
    track_data = getTrackData(itunes_id,country)
    if track_data is None:
        return None
    else:
        return getSpotifyId(track_data)

def check(station, playlist):
    radiko = requests.get("http://radiko.jp/v3/feed/pc/noa/" + station + ".xml")
    radiko.encoding = radiko.apparent_encoding
    radiko_xml = ElementTree.fromstring(radiko.text)

    ids = []
    for radiko_item in radiko_xml[1].iter('item'):
        if radiko_item.attrib['itunes'] is not "":
            itunes_url = parse.urlparse(radiko_item.attrib['itunes'])
            itunes_id = parse.parse_qs(itunes_url.query)["i"][0]
            spotify_id = getSpotifyId_itunes(itunes_id,"JP")
            if spotify_id is None:
                spotify_id = getSpotifyId_itunes(itunes_id,"US")
                if spotify_id is None:
                    spotify_id = getSpotifyId(getTrackData_radiko(radiko_item))
        else:
            spotify_id = getSpotifyId(getTrackData_radiko(radiko_item))

        if spotify_id is not None:
            ids.append(spotify_id)

        print(getTrackData_radiko(radiko_item), spotify_id)

    query_data = []
    for id in ids:
        query_data.append({
            "uri":"spotify:track:" + id
        })
    
    requests.delete(
        "https://api.spotify.com/v1/playlists/" + playlist + "/tracks", 
        json = { "tracks" : query_data },
        headers = { 
            'Authorization': 'Bearer ' + access_token,
            "Content-Type" : "application/json"
        }
    )

    query_data = []
    for id in ids:
        query_data.append("spotify:track:" + id)

    requests.post(
        "https://api.spotify.com/v1/playlists/" + playlist + "/tracks", 
        json = {
            "uris" : query_data,
            "position": 0
        },
        headers = { 
            'Authorization': 'Bearer ' + access_token,
            "Content-Type" : "application/json"
        }
    )

access_token = json.loads(
    requests.post(
        "https://accounts.spotify.com/api/token",
        data = {
            "grant_type" : "refresh_token",
            "refresh_token" : config.refresh_token
        },
        headers = {
            "Authorization" : "Basic " + base64.b64encode((config.client_token+":"+config.client_secret).encode()).decode()
        }
    ).text)["access_token"]

check("TBS", "11OVi6X97j56J64adgdF5o")
check("QRR", "304jv8dR1DnFveTH969ObD")
check("RN2", "0MZ068JyJDhdOGDoAc1LML")
check("INT", "6ql2qiuO69kjTZK8FZzDyJ")
check("FMT", "0hzw8H4PSmFDd0K952AjT7")
check("FMJ", "2dK6F6vzYm9yfPI7MCkAb7")
check("BAYFM78", "0AzldR8iNos8ZpUDc6uQUu")
check("NACK5", "4bznTT4izxtHxWJNnEo6lL")
check("YFM", "0YEpGbfFBxo04HGIQzldMM")
