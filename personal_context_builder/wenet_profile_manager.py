""" Module responsibles to communicate with Wenet profile manager, to fill the profiles with
    the routines
"""
from personal_context_builder import config
import requests
from pprint import pprint


class PersonalBehavior(object):
    def __init__(self, routine):
        self.id = ""
        self.label = ""
        self.proximity = ""
        self.from_time = 0
        self.to_time = 2359


def update_profile(routines, profile_id, url=config.DEFAULT_PROFILE_MANAGER_URL):
    profile_url = url + f"/profiles/{profile_id}"
    personal_behaviors = [PersonalBehavior(routine).__dict__ for routine in routines]
    #  r = requests.put(profile_url, data={"personalBehaviors": personal_behaviors})
    print(f"send to {profile_url}: \n")
    for p in personal_behaviors:
        pprint(p)

    print()
