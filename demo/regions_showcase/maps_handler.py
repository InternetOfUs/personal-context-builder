"""
module that handle maps
"""

import requests


class MapsHandler(object):
    def __init__(self, key_file):
        with open(key_file, "r") as f:
            self._key = f.read()
        self._base_url = "https://maps.googleapis.com/maps/api/staticmap?size=600x600&"
        self._end_url = f"key={self._key}"

    def static_from_locations(self, locations):
        markers = "|".join([f"{l._lat},{l._lng}" for l in locations])
        url = f"{self._base_url}markers={markers}&{self._end_url}"
        r = requests.get(url)
        return r.content

    def static_from_regions(self, locations_list):
        locations_str = ""
        for locations in locations_list:
            path = "|".join([f"{l._lat},{l._lng}" for l in locations])
            locations_str += (
                "&path=color:0x00000000|weight:5|fillcolor:0xFFFF0033|" + path
            )
        url = f"{self._base_url}{locations_str[1:]}&{self._end_url}"
        r = requests.get(url)
        return r.content
