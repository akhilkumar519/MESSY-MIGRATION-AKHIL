import os
from app import create_app
from application.database import init_db, get_db 
from application.utils.security import hash_password 


app = create_app()


with app.app_context():
    # Ensure the database file is clean before initializing
    db_path = app.config['DATABASE']
    if os.path.exists(db_path):
        print(f"Removing existing database: {db_path}")
        os.remove(db_path)

    print("Initializing the database...")
    init_db() 
    print("Database initialized successfully!")

    print("Populating with sample data...")
    db = get_db()
    cursor = db.cursor()

    # Sample users (passwords will be hashed)
    sample_users = [
        ("Alice Smith", "alice@example.com", "password123"),
        ("Bob Johnson", "bob@example.com", "securepass"),
        ("Charlie Brown", "charlie@example.com", "mysecret")
    ]

    for name, email, password in sample_users:
        hashed_pw = hash_password(password)
        if hashed_pw:
            try:
                cursor.execute(
                    "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                    (name, email, hashed_pw)
                )
                print(f"  Added user: {name}")
            except Exception as e:
                print(f"  Error adding user {name}: {e}")
        else:
            print(f"  Failed to hash password for {name}, skipping.")

    db.commit() # Commit all sample data insertions
    print("Sample data population complete.")