import sqlite3
import bcrypt
import pandas as pd
from pathlib import Path
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.ensure_tables()
    
    def get_connection(self):
        """Get database connection."""
        return sqlite3.connect(str(self.db_path))
    
    def ensure_tables(self):
        """Ensure all required tables exist."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Cyber incidents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cyber_incidents (
                incident_id INTEGER PRIMARY KEY,
                timestamp TEXT,
                severity TEXT,
                category TEXT,
                status TEXT,
                description TEXT
            )
        ''')
        
        # Datasets metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS datasets_metadata (
                dataset_id TEXT PRIMARY KEY,
                name TEXT,
                category TEXT,
                num_records INTEGER,
                last_updated TEXT
            )
        ''')
        
        # IT tickets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS it_tickets (
                ticket_id INTEGER PRIMARY KEY,
                priority TEXT,
                description TEXT,
                status TEXT,
                assigned_to TEXT,
                created_at TEXT,
                resolution_time_hours INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def verify_user(self, username, password):
        """Verify user credentials."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, username, password_hash, role FROM users WHERE username = ?",
            (username,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            user_id, username, stored_hash, role = result
            # Verify password against bcrypt hash
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                return {
                    'id': user_id,
                    'username': username,
                    'role': role
                }
        return None
    
    def user_exists(self, username):
        """Check if username exists."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM users WHERE username = ?",
            (username,)
        )
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def register_user(self, username, password, role="user"):
        """Register new user with bcrypt password hashing."""
        try:
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role)
            )
            conn.commit()
            conn.close()
            return True, "Account created successfully!"
        except sqlite3.IntegrityError:
            return False, "Username already exists"
        except Exception as e:
            return False, f"Registration failed: {str(e)}"
    
    def get_user_role(self, username):
        """Get user role from database."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role FROM users WHERE username = ?",
            (username,)
        )
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else "user"
    
    def get_cyber_incidents(self):
        """Get all cyber incidents."""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM cyber_incidents", conn)
        conn.close()
        return df
    
    def get_datasets_metadata(self):
        """Get all datasets metadata."""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM datasets_metadata", conn)
        conn.close()
        return df
    
    def get_it_tickets(self):
        """Get all IT tickets."""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM it_tickets", conn)
        conn.close()
        return df
    
    def add_cyber_incident(self, severity, category, description):
        """Add new cyber incident."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Generate incident ID
        cursor.execute("SELECT MAX(incident_id) FROM cyber_incidents")
        max_id = cursor.fetchone()[0] or 1000
        new_id = max_id + 1
        
        cursor.execute('''
            INSERT INTO cyber_incidents 
            (incident_id, timestamp, severity, category, status, description)
            VALUES (?, datetime('now'), ?, ?, 'Open', ?)
        ''', (new_id, severity, category, description))
        
        conn.commit()
        conn.close()
        return new_id
    
    def update_incident_status(self, incident_id, new_status):
        """Update incident status."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE cyber_incidents SET status = ? WHERE incident_id = ?",
            (new_status, incident_id)
        )
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return rows_affected > 0