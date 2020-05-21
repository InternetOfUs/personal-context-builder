""" Module responsibles to communicate with Wenet profile manager, to fill the profiles with
    the routines
"""
from personal_context_builder import config
from regions_builder.data_loading import BaseSourceLocations, BaseSourceLabels
from regions_builder.models import LocationPoint, UserPlaceTimeOnly, UserLocationPoint
from personal_context_builder.wenet_logger import create_logger
from personal_context_builder import wenet_exceptions
import datetime
import pandas as pd
import requests
from collections import defaultdict
from pprint import pprint


class Label(object):
    def __init__(self, name, semantic_class, latitude, longitude):
        self.name = name
        self.semantic_class = semantic_class
        self.latitude = latitude
        self.longitude = longitude


class ScoredLabel(object):
    def __init__(self, score, label):
        self.label = label
        self.score = score


class PersonalBehavior(object):
    def __init__(self, user_id, weekday, confidence):
        self.user_id = user_id
        self.weekday = weekday
        self.confidence = confidence
        self.label_distribution = defaultdict(list)

    def fill(self, routines):
        #  TODO something with routines
        pass


def update_profile(routines, profile_id, url=config.DEFAULT_PROFILE_MANAGER_URL):
    profile_url = url + f"/profiles/{profile_id}"
    personal_behaviors = []
    #  r = requests.put(profile_url, data={"personalBehaviors": personal_behaviors})
    print(f"send to {profile_url}: \n")
    for p in personal_behaviors:
        pprint(p)

    print()
