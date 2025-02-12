from werkzeug.security import generate_password_hash, check_password_hash
from app.configs.database import db
from datetime import datetime, timedelta, timezone
from app.models.user import User
from app.services.email import send_email
import uuid
import jwt
from flask import url_for

# 🔹 SECRET KEY (Consider using environment variables)
SECRET_KEY = "YOUR_SECRET_KEY"
REACT_BASE_URL = 'http://localhost:5173'

# 🔹 REGISTER USER
def register_user(email, password):
    email = email.lower().strip()  # Normalize email
    user = User.query.filter_by(email=email).first()
    
    hashed_password = generate_password_hash(password)
    verification_token = str(uuid.uuid4())
    verify_url = f'{REACT_BASE_URL}/?token={verification_token}'
    token_expiry = datetime.now(timezone.utc) + timedelta(minutes=10)

    if user:
        if user.isVerified:
            return {"success": False, "message": "User already exists."}
        # If user exists but is not verified, update token & send email
        user.password = hashed_password
        user.verification_token = verification_token
        user.verification_token_expiry = token_expiry
        db.session.commit()
        send_email("Verification Email", email, f"Your verification URL is {verify_url}")
        return {"success": True}

    # Create new unverified user
    new_user = User(
        email=email,
        password=hashed_password,
        isVerified=False,  # Default: Not verified
        verification_token=verification_token,
        verification_token_expiry=token_expiry
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    send_email("Verification Email", email, f"Your verification URL is {verify_url}")
    return {"success": True, "message": "User registered successfully. Check your email for verification."}

# 🔹 AUTHENTICATE USER (LOGIN)
def authenticate_user(email, password):
    email = email.lower().strip()  # Normalize email
    user = User.query.filter_by(email=email).first()

    if not user:
        return {"success": False, "message": "User not found."}
    
    if not user.isVerified:
        return {"success": False, "message": "Please verify your email before logging in."}
    
    if check_password_hash(user.password, password):
        payload = {"user_id": user.id}
        access_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        
        user.token = access_token
        db.session.commit()

        return {"success": True, "message": access_token}
    
    return {"success": False, "message": "Invalid email or password."}
