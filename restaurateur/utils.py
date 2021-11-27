import requests

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from requests import HTTPError

from place.models import Place


class NoPlaceFound(Exception):
    pass


def get_coordinates(address):
    try:
        place = Place.objects.get(address=address)
    except ObjectDoesNotExist:
        try:
            coords = fetch_coordinates_from_yandex_api(address)
        except (HTTPError, NoPlaceFound):
            coords = [0, 0]
        finally:
            place = Place(address=address, latitude=coords[1], longitude=coords[0])
            place.save()

    return place.longitude, place.latitude


def fetch_coordinates_from_yandex_api(address):
    apikey = settings.YANDEX_API_KEY
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        raise NoPlaceFound

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat
