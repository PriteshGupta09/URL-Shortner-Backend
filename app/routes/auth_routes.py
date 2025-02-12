from flask import Blueprint, request, jsonify, make_response, url_for
from flask_jwt_extended import unset_jwt_cookies
from datetime import datetime, timedelta, timezone
from app.controllers.auth import register_user, authenticate_user
from app.models.user import User
from app.configs.database import db
import uuid
from app.services.email import send_email
from werkzeug.security import generate_password_hash

auth_bp = Blueprint("auth", __name__)

REACT_BASE_URL = 'http://localhost:5173'

# 🔹 REGISTER USER
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    confirm_password = data.get("confirm_password")

    if not all([email, password, confirm_password]):
        return jsonify({"message": "Missing required fields", "success": False}), 400

    if password != confirm_password:
        return jsonify({"message": "Passwords do not match", "success": False}), 400

    if not (8 <= len(password) <= 16):
        return jsonify({"message": "Password must be between 8 and 16 characters", "success": False}), 400

    new_user = register_user(email, password)
    if new_user["success"]:
        return jsonify({"message": "Email sent successfully", "success": True}), 200
    return jsonify({"message": new_user["message"], "success": False}), 400

# 🔹 LOGIN USER
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return jsonify({"message": "Missing credentials", "success": False}), 400

    access_token = authenticate_user(email, password)

    if not access_token["success"]:
        return jsonify({"message": access_token["message"], "success": False}), 400

    response = make_response(jsonify({"message": "Login successful", "success": True}), 200)
    response.set_cookie(
        "token",
        access_token["message"],
        secure=False,  # Set to True for production (HTTPS)
        samesite=None,
        max_age=86400  # 1 day
    )
    return response

# 🔹 VERIFY EMAIL
@auth_bp.route("/verify", methods=["POST"])
def verify_email():
    data = request.json
    token = data.get("token")

    if not token:
        return jsonify({"message": "Token not found", "success": False}), 400

    user = User.query.filter_by(verification_token=token).first()
    utc_now = datetime.now(timezone.utc)

    if not user or user.verification_token_expiry < utc_now:
        return jsonify({"message": "Invalid or expired token", "success": False}), 400

    user.isVerified = True
    user.verification_token = None
    user.verification_token_expiry = None
    db.session.commit()

    return jsonify({"message": "Email verified successfully!", "success": True}), 200

# 🔹 FORGOT PASSWORD
@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"message": "Missing credentials", "success": False}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "User not found", "success": False}), 400

    reset_token = str(uuid.uuid4())
    reset_url = f'{REACT_BASE_URL}/?token={reset_token}'
    send_email("Reset Your Password", email, f"Click the link to reset: {reset_url}")

    user.reset_password_token = reset_token
    user.reset_token_expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
    db.session.commit()

    return jsonify({"message": "Password reset link sent to your email", "success": True}), 200

# 🔹 RESET PASSWORD
@auth_bp.route("/verify-forgot-password", methods=["POST"])
def verify_forgot_password():
    data = request.json
    token = data.get("token")

    if not token:
        return jsonify({"message": "Missing credentials", "success": False}), 400

    user = User.query.filter_by(reset_password_token=token).first()
    utc_now = datetime.now(timezone.utc)

    if not user or user.reset_token_expiry < utc_now:
        return jsonify({"message": "Invalid or expired token", "success": False}), 400

    return jsonify({"message": "Token verified successful", "success": True}), 200

@auth_bp.route('/new-password' , methods=['POST'])
def new_password_func():
    data = request.json
    token = data.get("token")
    password = data.get("password")
    new_password = data.get("new_password")

    if not all([token, password, new_password]):
        return jsonify({"message": "Missing credentials", "success": False}), 400

    if not (8 <= len(password) <= 16):
        return jsonify({"message": "Password must be between 8 and 16 characters", "success": False}), 400

    if password != new_password:
        return jsonify({"message": "Passwords do not match", "success": False}), 400

    user = User.query.filter_by(reset_password_token=token).first()
    utc_now = datetime.now(timezone.utc)

    if not user or user.reset_token_expiry < utc_now:
        return jsonify({"message": "Invalid or expired token", "success": False}), 400

    user.password = generate_password_hash(new_password)
    user.reset_password_token = None
    user.reset_token_expiry = None
    db.session.commit()

    return jsonify({"message": "Password reset successful", "success": True}), 200

# 🔹 LOGOUT USER
@auth_bp.route("/logout", methods=["POST"])
def logout():
    response = make_response(jsonify({"message": "Logged out", "success": True}), 200)
    # Unset JWT cookies
    unset_jwt_cookies(response)
    # Explicitly clear cookies
    response.set_cookie(
        "token", "", expires=0, httponly=True, secure=True, samesite="None"
    )
    
    return response
