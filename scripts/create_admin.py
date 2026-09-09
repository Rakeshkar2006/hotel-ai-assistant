from getpass import getpass

from sqlalchemy import select

from app.core.security import hash_password
from app.db.models.user import User
from app.db.session import SessionLocal


def create_admin():
    print("=== Create Admin User ===")

    email = input("Admin email: ").strip()
    full_name = input("Admin full name: ").strip()
    password = getpass("Admin password: ")

    if not email or not full_name or not password:
        print("Error: All fields are required.")
        return

    db = SessionLocal()

    try:
        existing_user = db.scalar(
            select(User).where(User.email == email)
        )

        if existing_user:
            print("Error: This email is already registered.")
            return

        admin = User(
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),
            role="admin",
            is_active=True,
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print()
        print("Admin user created successfully!")
        print(f"ID: {admin.id}")
        print(f"Email: {admin.email}")
        print(f"Name: {admin.full_name}")
        print(f"Role: {admin.role}")

    except Exception as error:
        db.rollback()
        print(f"Error creating admin: {error}")

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()