"""
Module that handle database access for user's profile
"""
import config
import redis
import json

_REDIS_SERVER = redis.Redis(
    host=config.DEFAULT_REDIS_HOST, port=config.DEFAULT_REDIS_PORT, db=0
)


def clean_db():
    """ clean the db (delete all entries)
    """
    for key in _REDIS_SERVER.scan_iter():
        _REDIS_SERVER.delete(key)


def delete_profile(user_id):
    """ delete a profile
    Args:
        user_id: user_id of the profile
    """
    _REDIS_SERVER.delete(user_id)


def get_all_profiles(match=None):
    """ get all profiles
    Args:
        match: pattern to retreive the profiles (not regex)
    Return:
        dict with user_id -> vector
    """
    my_dict = dict()
    for key in _REDIS_SERVER.scan_iter(match=match):
        my_dict[key.decode("utf-8")] = json.loads(_REDIS_SERVER.get(key))
    return my_dict


def get_profile(user_id):
    """ get a specific profile
    Args:
        user_id: user_id of the profile
    Return:
        a vector (list of float)
    """
    res = _REDIS_SERVER.get(user_id)
    if res is None:
        return res
    return json.loads(res)


def set_profile(user_id, vector):
    """ create or modify a profile
    Args:
        user_id: user_id of the profile
        vector: list of float for that profile
    """
    value = json.dumps(vector)
    _REDIS_SERVER.set(user_id, value)


def set_profiles(user_ids, vectors):
    """ create or modify multiple profiles at once

    The function use the pipeline object for better performance

    Args:
        user_ids: list of user_id
        vectors: list of vector
    """
    pipeline = _REDIS_SERVER.pipeline()
    for user_id, vector in zip(user_ids, vectors):
        value = json.dumps(vector)
        pipeline.set(user_id, value)
    pipeline.execute()
