import bcrypt
import sqlite3
from pathlib import Path
from ..data.db import connect_database
from ..data.users import get_user_by_username, insert_user
from ..data.schema import create_users_table
def register_user(username, password, role='user'):
    """Register new user with password hashing."""
    # Hash password
    password_hash = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    
    # Insert into database
    insert_user(username, password_hash, role)
    return True, f"User '{username}' registered successfully."
def login_user(username, password):
    """Authenticate user."""
    user = get_user_by_username(username)
    if not user:
        return False, "User not found."
    
    # Verify password
    stored_hash = user[2]  # password_hash column
    if bcrypt.checkpw(password.encode('utf-8'), 
stored_hash.encode('utf-8')):
        return True, f"Login successful!"
    return False, "Incorrect password."
def migrate_users_from_file(filepath="users.txt"):
    """
    Migrate users from users.txt to the database.
    
    Args:
        filepath: Path to users.txt file
        
    Returns:
        int: Number of users migrated
    """
    conn = connect_database()
    path = Path(filepath)
    
    # Check if file exists
    if not path.exists():
        print(f"Warning: {filepath} not found. Skipping migration.")
        return 0
    
    cursor = conn.cursor()
    migrated_count = 0
    
    # Read the file line by line
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            
            # Parse the line
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 2:
                continue
            
            username = parts[0]
            password_hash = parts[1]
            role = parts[2] if len(parts) >= 3 else "user"
            
            # Insert into database using parameterized query
            try:
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    (username, password_hash, role)
                )
                migrated_count += 1
            except sqlite3.IntegrityError:
                # User already exists (username is UNIQUE)
                print(f" User '{username}' already exists. Skipping.")
    
    conn.commit()
    conn.close()
    return migrated_count