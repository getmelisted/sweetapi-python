from functools import wraps

from flask import Response, request

from lib import config


__author__ = 'pat'


def is_valid_api_key(key):
    """Validates received API key"""
    return key == config.local_api_key


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response('Invalid or missing API key', 403)


def extract_api_key_from_request(req):
    """Extracts the api_key value from either the GET params, or body params"""
    return req.values.get('api_key')


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = extract_api_key_from_request(request)
        if not is_valid_api_key(api_key):
            return authenticate()
        return f(*args, **kwargs)

    return decorated