"""
Module that handle database access for user's profile
"""
import config
import redis
import json

_REDIS_SERVER = redis.Redis(
    host=config.DEFAULT_REDIS_HOST, port=config.DEFAULT_REDIS_PORT, db=0
)


def delete_profile(user_id):
    _REDIS_SERVER.delete(user_id)


def get_all_profiles():
    pass


def get_profile(user_id):
    res = _REDIS_SERVER.get(user_id)
    if res is None:
        return res
    return json.loads(res)


def set_profile(user_id, vector):
    value = json.dumps(vector)
    _REDIS_SERVER.set(user_id, value)