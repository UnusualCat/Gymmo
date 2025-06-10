from functools import wraps
from flask import abort # Changed from flask import current_app, abort to just abort
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            # current_app.logger.warning(f"Admin access denied for user {current_user.username if current_user.is_authenticated else 'Anonymous'}")
            abort(403) # Forbidden
        return f(*args, **kwargs)
    return decorated_function
