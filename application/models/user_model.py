import sqlite3
from application.database import get_db

class UserModel:
    
    def get_all_users(self):
       
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, email FROM users") 
        return [dict(row) for row in cursor.fetchall()]

    def get_user_by_id(self, user_id):
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        return dict(user) if user else None

    def get_user_by_email(self, email):
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, email, password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        return dict(user) if user else None
    
    def get_user_by_name(self, name):
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
        user = cursor.fetchone()
        return dict(user) if user else None

    def create_user_db(self, name, email, hashed_password):
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, hashed_password)
        )
        db.commit()
        return cursor.lastrowid # Returns the ID of the newly inserted row

    def update_user_db(self, user_id, name, email):
       
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE users SET name = ?, email = ? WHERE id = ?",
            (name, email, user_id)
        )
        db.commit()
        return cursor.rowcount > 0 # rowcount indicates number of rows affected

    def delete_user_db(self, user_id):
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        db.commit()
        return cursor.rowcount > 0

    def search_users_by_name_db(self, name_query):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, email FROM users WHERE name LIKE ?", ('%' + name_query + '%',))
        return [dict(row) for row in cursor.fetchall()]