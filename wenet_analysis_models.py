"""
models (ML sense) used for create user profile
"""
import config
import pickle
from functools import partial

from sklearn.decomposition import LatentDirichletAllocation


class BaseModel(object):
    def predict(self, *args, **kwargs):
        raise NotImplementedError("not implemented")

    def transform(self, *args, **kwargs):
        raise NotImplementedError("not implemented")

    def fit(self, *args, **kwargs):
        raise NotImplementedError("not implemented")


class BaseModelWrapper(BaseModel):
    def __init__(self, model_class, name="unamed"):
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
        with open(filename, "wb") as f:
            dump_fct(self.__dict__, f)

    @staticmethod
    def load(filename=config.DEFAULT_ANALYSIS_MODEL_FILE, load_fct=pickle.load):
        """ Create a instance of BaseModelWrapper from a previously saved file
            Args:
                filename: file that contain the saved BaseModelWrapper instance
                load_fct: function to use to load the instance from a file
            Return:
                An instance of BaseModelWrapper
        """
        with open(filename, "rb") as f:
            wrapper = BaseModelWrapper(None)
            wrapper.__dict__ = load_fct(f)
            return wrapper


class SimpleLDA(BaseModelWrapper):
    def __init__(self, n_components=15, random_state=0, n_jobs=-1, **kwargs):
        my_lda = partial(
            LatentDirichletAllocation,
            n_components=15,
            random_state=0,
            n_jobs=-1,
            **kwargs
        )
        super().__init__(my_lda, "simple_lda.p")

    def predict(self, *args, **kwargs):
        return super().transform(*args, **kwargs)
