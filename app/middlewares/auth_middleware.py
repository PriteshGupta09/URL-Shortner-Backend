from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

def jwt_required_middleware(func):
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
        except Exception as e:
            return jsonify({"error": "Unauthorized"}), 401
        
        return func(user_id, *args, **kwargs)
    return wrapper
