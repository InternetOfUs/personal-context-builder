"""
models (ML sense) used for create user profile
"""
import config
import pickle


class BaseModel(object):
    def predict(self, *args, **kwargs):
        return self.transform(*args, **kwargs)

    def transform(self, *args, **kwargs):
        raise NotImplementedError("not implemented")

    def fit(self, *args, **kwargs):
        raise NotImplementedError("not implemented")


class BaseModelWrapper(BaseModel):
    def __init__(self, model_class, name="unamed"):
        self._model_class = model_class
        self._name = name
        self._model_instance = None

    def transform(self, *args, **kwargs):
        if self._model_instance is None:
            raise Exception(
                "model has to be loaded of trained before transform/predict"
            )
        return self._model_instance.transform(*args, **kwargs)

    def fit(self, *args, **kwargs):
        self._model_instance = self._model_class(*args, **kwargs)

    def save(self, filename=config.DEFAULT_ANALYSIS_MODEL_FILE, dump_fct=pickle.dump):
        with open(filename, "wb") as f:
            dump_fct(self.__dict__, f)

    @staticmethod
    def load(filename=config.DEFAULT_ANALYSIS_MODEL_FILE, load_fct=pickle.load):
        with open(filename, "rb") as f:
            wrapper = BaseModelWrapper(None)
            wrapper.__dict__ = load_fct(f)
            return wrapper
