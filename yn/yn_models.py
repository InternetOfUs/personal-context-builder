"""
module for Y@N specific models

Use wenet models as bases
"""

import wenet_models as wm


class User(object):
    """ Y@N user information
    """

    def __init__(self):
        self._user_id = ""
        self._stay_points = []
        self._stay_regions = []


class YNStayPoint(wm.StayPoint):
    pass


class YNLabelledStayRegion(wm.LabelledStayRegion):
    pass
