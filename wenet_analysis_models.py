"""
models (ML sense) used for create user profile
"""
import config
import pickle
from functools import partial
from os.path import join

import numpy as np
from sklearn.decomposition import LatentDirichletAllocation


class BaseModel(object):
    def predict(self, *args, **kwargs):
        raise NotImplementedError("not implemented")

    def transform(self, *args, **kwargs):
        raise NotImplementedError("not implemented")

    def fit(self, *args, **kwargs):
        raise NotImplementedError("not implemented")


class BaseModelWrapper(BaseModel):
    def __init__(self, model_class=None, name="unamed"):
        self._model_class = model_class
        self._name = name
        if model_class is not None:
            self._model_instance = self._model_class()
        else:
            self._model_instance = None

    def transform(self, *args, **kwargs):
        if self._model_instance is None:
            raise Exception("model has to be loaded of trained before transform")
        return self._model_instance.transform(*args, **kwargs)

    def predict(self, *args, **kwargs):
        if self._model_instance is None:
            raise Exception("model has to be loaded of trained before predict")
        return self._model_instance.predict(*args, **kwargs)

    def fit(self, *args, **kwargs):
        self._model_instance.fit(*args, **kwargs)

    def save(self, filename=config.DEFAULT_ANALYSIS_MODEL_FILE, dump_fct=pickle.dump):
        """ save this current instance of BaseModelWrapper
            Args:
                filename: file that will be used to store the instance
                dump_fct: function to use to dump the instance into a file
        """
        location = join(config.DEFAULT_DATA_FOLDER, filename)
        with open(location, "wb") as f:
            dump_fct(self.__dict__, f)

    @classmethod
    def load(cls, filename=config.DEFAULT_ANALYSIS_MODEL_FILE, load_fct=pickle.load):
        """ Create a instance of BaseModelWrapper from a previously saved file
            Args:
                filename: file that contain the saved BaseModelWrapper instance
                load_fct: function to use to load the instance from a file
            Return:
                An instance of BaseModelWrapper
        """
        location = join(config.DEFAULT_DATA_FOLDER, filename)
        with open(location, "rb") as f:
            wrapper = cls()
            wrapper.__dict__ = load_fct(f)
            return wrapper


class SimpleLDA(BaseModelWrapper):
    def __init__(
        self, name="simple_lda", n_components=15, random_state=0, n_jobs=-1, **kwargs
    ):
        my_lda = partial(
            LatentDirichletAllocation,
            n_components=15,
            random_state=0,
            n_jobs=-1,
            **kwargs
        )
        super().__init__(my_lda, name)

    def predict(self, *args, **kwargs):
        return super().transform(*args, **kwargs)


class SimpleBOW(BaseModelWrapper):
    def __init__(self, name="simple_bow"):
        super().__init__(None, name)

    def transform(self, *args, **kwargs):
        return self.predict(*args, **kwargs)

    def predict(self, *args, **kwargs):
        X = args[0]
        return np.mean(X, axis=0)

    def fit(self, *args, **kwargs):
        pass
