from flask import Blueprint, request, jsonify
from database.connection import SessionLocal
from database.models import User
from Backend.authentication import hash_password, verify_password

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    db = SessionLocal()

    try:
        data = request.get_json()

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not name or not email or not password:
            return jsonify({"error": "All fields are required"}), 400

        existing_user = db.query(User).filter_by(email=email).first()

        if existing_user:
            return jsonify({"error": "Email already registered"}), 409

        new_user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role="citizen"
        )

        db.add(new_user)
        db.commit()

        return jsonify({
            "message": "Registration successful",
            "user_id": new_user.user_id
        }), 201

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        db.close()