from urllib import parse
from xml.etree import ElementTree

import requests

import format


def fetch(station: str):
    res = requests.get(
        "http://radiko.jp/v3/feed/pc/noa/" + station + ".xml")
    res.encoding = res.apparent_encoding
    return ElementTree.fromstring(res.text)


def get_station_name(xml):
    return xml.find('station').text


def extract_itunes_id(item):
    if item.attrib['itunes'] == "":
        return None
    itunes_url = parse.urlparse(item.attrib['itunes'])
    parsed_query = parse.parse_qs(itunes_url.query)
    if 'i' not in parsed_query:
        return None
    return parsed_query["i"][0]


def get_detail(item):
    return (
        format.format(item.attrib['artist']),
        "",
        format.format(item.attrib['title'])
    )
