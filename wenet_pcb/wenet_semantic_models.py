""" module that contains sematic model for the predictions

-  Train on history of the user days with locations and labels
-  Should be able to predict labels probabilities for each time slot for each weekday
-  Should be able to give scores/metrics for validation
"""


class SemanticModel(object):
    def __init__(self, locations_source, labels_source, name="unknown_semantic_model"):
        """ Constructor
        Args:
            locations_source: source of the locations
            labels_sources: source of the labels
            name: name of the model
        """
        self._locations_source = locations_source
        self._labels_source = labels_source
        self._name = name

    def compute_weekdays(self, user_id):
        """ Compute the all weekday distributions for the given user
        Args:
            user_id: for which user the weekday are computed

        Return: Distribution of the labels for each day for each time slots
        """
        pass
