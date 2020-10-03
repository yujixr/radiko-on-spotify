import json

import requests

import format


def get_detail(itunes_id, country):
    res = requests.get(
        "http://ax.itunes.apple.com/WebObjects/MZStoreServices.woa/wa/wsLookup",
        params={
            "id": itunes_id,
            "country": country
        }
    ).text
    res_json = json.loads(res)

    if res_json["resultCount"] == 0:
        return None
    return (
        format.format(res_json["results"][0]["artistName"]),
        format.format(res_json["results"][0]["collectionCensoredName"]),
        format.format(res_json["results"][0]["trackCensoredName"])
    )
