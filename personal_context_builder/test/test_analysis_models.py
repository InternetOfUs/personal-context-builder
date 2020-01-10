import unittest
from os import remove
from os.path import join
from sklearn.datasets import load_iris
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from personal_context_builder.wenet_analysis_models import BaseModelWrapper
from functools import partial
from personal_context_builder import config


class UserProfileDBTestCase(unittest.TestCase):
    def setUp(self):
        self.model_1 = "model_1.bin"

    def test_simple_model(self):
        iris = load_iris()
        X = iris.data
        y = iris.target
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.33, random_state=42
        )
        my_svn = partial(SVC, random_state=42)
        my_wrapper = BaseModelWrapper(my_svn, "simple SVN")
        my_wrapper.fit(X_train, y_train)
        prediction_1 = my_wrapper.predict(X_test)
        my_wrapper.save(self.model_1)
        my_wrapper2 = BaseModelWrapper.load(self.model_1)
        prediction_2 = my_wrapper2.predict(X_test)
        self.assertTrue((prediction_1 == prediction_2).all())

    def tearDown(self):
        location = join(config.DEFAULT_DATA_FOLDER, self.model_1)
        remove(location)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
