""" Module responsibles to communicate with Wenet profile manager, to fill the profiles with
    the routines
"""
from personal_context_builder import config


class PersonalBehavior(object):
    def __init__(self, routine):
        self.id = ""
        self.label = ""
        self.proximity = ""
        self.from_time = 0
        self.to_time = 2359


def update_profile(routines, url=config.DEFAULT_PROFILE_MANAGER_URL):
    pass
