from requests import HTTPError

from place.models import Place
from place.yandex_geocoder_api import fetch_coordinates_from_yandex_api, PlaceDoesNotResolvedByGeocoder


def get_places(addresses):
    places = Place.objects.in_bulk(addresses, field_name='address')
    not_existed_addresses = [a for a in addresses if a not in places.keys()]
    for address in not_existed_addresses:
        places[address] = create_place(address)
    return places


def create_place(address):
    try:
        coords = fetch_coordinates_from_yandex_api(address)
    except (HTTPError, PlaceDoesNotResolvedByGeocoder):
        coords = [0, 0]
    finally:
        place = Place(address=address, latitude=coords[1], longitude=coords[0])
        place.save()

    return place.longitude, place.latitude

