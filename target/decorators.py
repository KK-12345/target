import logging
from functools import wraps

from flask import request, make_response, g, jsonify

from models import User
from target.settings.backend import DBBackend


def token_error(message=None):
    response = dict()
    response['data'] = "Missing or Invalid token" if not message else message
    response["status"] = "failure"
    response_code = 401
    return make_response(jsonify(response)), response_code


def verify_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        try:
            token = auth_header.split(" ")[1]
            decoded_token = User.decode_token(token)
            if not isinstance(decoded_token, str):
                g.user_id = decoded_token
                session = DBBackend().get_session()
                user = session.query(User).filter_by(id=g.user_id).one()
                session.close()
                return f(*args, **kwargs)
            else:
                return token_error(decoded_token)
        except IndexError:
            return token_error()
        except AttributeError:
            return token_error()
        except Exception as ex:
            return token_error(ex)
    return decorated