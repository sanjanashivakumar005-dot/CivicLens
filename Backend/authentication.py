
from database.connection import SessionLocal
from database.models import User
from utils.helpers import hash_password, verify_password


def register_user(name, email, password, phone=None):
    """Register a new citizen account."""

    db = SessionLocal()

    try:
        existing_user = db.query(User).filter(User.email == email).first()

        if existing_user:
            return {
                "success": False,
                "message": "Email already registered"
            }

        new_user = User(
            name=name,
            email=email,
            phone=phone,
            password_hash=hash_password(password),
            role="citizen",
            is_active=True
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "success": True,
            "message": "Registration successful",
            "user_id": new_user.user_id
        }

    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"Registration failed: {str(e)}"
        }

    finally:
        db.close()


def login_user(email, password):
    """Authenticate an existing user."""

    db = SessionLocal()

    try:
        user = db.query(User).filter(User.email == email).first()

        # Check if user exists
        if not user:
            return {
                "success": False,
                "message": "Invalid email or password"
            }

        # Verify password using password_hash
        if not verify_password(password, user.password_hash):
            return {
                "success": False,
                "message": "Invalid email or password"
            }

        # Check if account is active
        if not user.is_active:
            return {
                "success": False,
                "message": "Account is inactive"
            }

        return {
            "success": True,
            "message": "Login successful",
            "user_id": user.user_id,
            "name": user.name,
            "role": user.role
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Login failed: {str(e)}"
        }

    finally:
        db.close()
