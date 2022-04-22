import requests
import sys
import os
import math

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
API_KEY = "40d1649f-0493-4b70-98ba-98533de7710b"


def geocode(adress):
    param = {
        'apikey': API_KEY,
        'geocode': adress,
        'format': 'json'
    }
    response = requests.get(geocoder_api_server, params=param)
    if response:
        response = response.json()
    else:
        raise RuntimeError(f'Ошибка выполнения запроса {geocoder_api_server}'
                           f'HTTP status: {response.status_code} ({response.reason})')
    return response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]


def get_cooords(adress):
    toponym = geocode(adress)
    if not toponym:
        return None, None
    return tuple(map(float, toponym['Point']['pos'].split()))


def get_ll_span(address):
    toponym = geocode(address)
    if not toponym:
        return (None, None)

    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    ll = ",".join([toponym_longitude, toponym_lattitude])

    envelope = toponym["boundedBy"]["Envelope"]

    l, b = envelope["lowerCorner"].split(" ")
    r, t = envelope["upperCorner"].split(" ")

    dx = abs(float(l) - float(r)) / 2.0
    dy = abs(float(t) - float(b)) / 2.0

    span = f"{dx},{dy}"

    return ll, span


def find_businesses(ll, spn, request, locale="ru_RU"):
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
    search_params = {
        "apikey": api_key,
        "text": request,
        "lang": locale,
        "ll": ll,
        "spn": spn,
        "type": "biz"
    }

    response = requests.get(search_api_server, params=search_params)
    if not response:
        raise RuntimeError(
            f"""Ошибка выполнения запроса:
            {search_api_server}
            Http статус: {response.status_code} ({response.reason})""")

    # Преобразуем ответ в json-объект
    json_response = response.json()

    # Получаем первую найденную организацию.
    organizations = json_response["features"]
    return organizations


def find_business(ll, spn, request, locale="ru_RU"):
    orgs = find_businesses(ll, spn, request, locale=locale)
    if len(orgs):
        return orgs[0]


def lonlat_distance(a, b):

    degree_to_meters_factor = 111 * 1000
    a_lon, a_lat = [float(i) for i in a]
    b_lon, b_lat = [float(i) for i in b]

    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    distance = math.sqrt(dx * dx + dy * dy)

    return distance


print(geocode('43.146478, 51.554601'))