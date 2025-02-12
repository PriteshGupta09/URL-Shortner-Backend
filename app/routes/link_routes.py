from flask import Flask, Blueprint, request, jsonify
from app.models.link import Link
from app.models.user import User
from app.configs.database import db
from app.services.DecodeJWT import DecodeJWT

link_gener = Blueprint('link', __name__)


# 🔹 READ USER LINKS
@link_gener.route('/read', methods=['POST'])
def read_link():
    user_id = DecodeJWT()
    if not user_id:
        return jsonify({"message": "Unauthorized access.", "success": False}), 400
    
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"message": "User not found.", "success": False}), 400

    return jsonify({"message": user.json, "success": True}), 200

# 🔹 CREATE A NEW SHORTLINK
@link_gener.route('/create', methods=['POST'])
def create_link():
    data = request.json or {}
    user_id = DecodeJWT()

    if not user_id:
        return jsonify({"message": "Unauthorized access.", "success": False}), 400
    
    required_fields = ["originalLink", "shortlink", "qrcode", "createdat"]

    missing_fields = [field for field in required_fields if field not in data or data[field] in [None, ""]]

    if "clicks" not in data:
        missing_fields.append("clicks")

    if missing_fields:
        return jsonify({
        "message": f"Missing credentials.",
        "success": False
        }), 400


    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"message": "User not found.", "success": False}), 400
    
    # Check for duplicate links
    links = user.json.get("links", [])

    for link in links:
        if link.get("originalLink") == data["originalLink"]:
            return jsonify({"message": "You already made a shortlink for this link.", "success": False}), 400
        if link.get("shortlink") == data["originalLink"]:
            return jsonify({"message": "Something went wrong, Try again.", "success": False}), 400

    # Create new link
    new_link = Link(
        originalLink=data["originalLink"],
        shortlink=data["shortlink"],
        qrcode=data["qrcode"],
        clicks=int(data["clicks"]),  # Ensure clicks is an integer
        user_id=user_id,
        createdat=data["createdat"]
    )

    db.session.add(new_link)
    db.session.commit()

    return jsonify({"message": "Link created successfully", "success": True}), 200

# 🔹 DELETE A SHORTLINK
@link_gener.route('/delete', methods=['POST'])
def delete_link():
    data = request.json or {}
    shortlink = data.get("shortlink")

    if not shortlink:
        return jsonify({"message": "Missing shortlink.", "success": False}), 400

    link = Link.query.filter_by(shortlink=shortlink).first()
    
    if not link:
        return jsonify({"message": "Shortlink not found.", "success": False}), 400

    db.session.delete(link)
    db.session.commit()

    return jsonify({"message": "Link deleted successfully", "success": True}), 200

# 🔹 UPDATE CLICK COUNT
@link_gener.route('/update-count', methods=['POST'])
def update_link():
    data = request.json or {}
    shortlink = data.get("shortlink")

    if not shortlink:
        return jsonify({"message": "Missing shortlink.", "success": False}), 400

    link = Link.query.filter_by(shortlink=shortlink).first()
    
    if not link:
        return jsonify({"message": "Shortlink not found.", "success": False}), 400

    link.clicks = (link.clicks or 0) + 1  # Ensure clicks is always a valid integer
    db.session.commit()

    return jsonify({"message": "Click count updated.", "success": True}), 200
