from utils import get_user_role, redirect
from flask import request, g
import logging 

def roles_required(roles: list, redirect_to=None):
    def decorator(f):
        def wrapper(*args, **kwargs):
            username = request.headers.get('X-Remote-User-Name')
            role = get_user_role(username)
            logging.debug(f"Username: {username}, Role: {role}")

            if role not in roles:
                return redirect('/')
            else:
                return f(*args, **kwargs)
        wrapper.__name__ = f.__name__ 
        return wrapper
    return decorator