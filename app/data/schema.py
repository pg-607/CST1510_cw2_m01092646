from pathlib import Path
import pandas as pd
from .db import connect_database

DATA_DIR = Path("DATA")

#might hv to change the fields
def create_users_table(conn):
    """
    Create the users table if it doesn't exist.
    
    Args:
        conn: Database connection object
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user'
    );
    """
    
    cursor = conn.cursor()
    cursor.execute(create_table_sql)
    conn.commit()
    print(" Users table created successfully!")

def create_cyber_incidents_table(conn):
    """Create the cyber_incidents table if it doesn't exist."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS cyber_incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        incident_id TEXT,
        timestamp TEXT NOT NULL,
        category TEXT,
        severity TEXT NOT NULL,
        status TEXT NOT NULL,
        description TEXT,
        reported_by TEXT
    );
    """
    
    cursor = conn.cursor()
    cursor.execute(create_table_sql)
    conn.commit()
    print(" Cyber Incidents table created successfully!")

def create_datasets_metadata_table(conn):
    """Create the datasets_metadata table if it doesn't exist."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS datasets_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset_id TEXT,
        name TEXT NOT NULL,
        rows INTEGER,
        columns INTEGER,
        uploaded_by TEXT,
        upload_date TEXT,
        description TEXT
    );
    """
    
    cursor = conn.cursor()
    cursor.execute(create_table_sql)
    conn.commit()
    print(" Datasets Metadata table created successfully!")

def create_it_tickets_table(conn):
    """Create the it_tickets table if it doesn't exist."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS it_tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id TEXT,
        priority TEXT,
        description TEXT,
        status TEXT NOT NULL,
        assigned_to TEXT,
        created_at TEXT,
        resolution_time_hours INTEGER
    );
    """
    
    cursor = conn.cursor()
    cursor.execute(create_table_sql)
    conn.commit()
    print(" IT Tickets table created successfully!")

def create_all_tables(conn):
    """Create all tables."""
    create_users_table(conn)
    create_cyber_incidents_table(conn)
    create_datasets_metadata_table(conn)
    create_it_tickets_table(conn)

def load_csv_to_table(conn, csv_path, table_name):
    """
    Load a CSV file into a database table using pandas.
    
    Args:
        conn: Database connection
        csv_path: Path to CSV file
        table_name: Name of the database table
        
    Returns:
        int: Number of rows loaded
    """
    path = Path(csv_path)
    
    # Check if file exists
    if not path.exists():
        print(f" Warning: {csv_path} not found. Skipping.")
        return 0
    
    # Read CSV into DataFrame
    df = pd.read_csv(path)
    
    # Clean column names (remove extra whitespace)
    df.columns = df.columns.str.strip()
    
    # Map CSV columns to database columns for cyber_incidents
    if table_name == 'cyber_incidents':
        column_mapping = {
            'incident_id': 'incident_id',
            'timestamp': 'timestamp',
            'category': 'category',
            'severity': 'severity',
            'status': 'status',
            'description': 'description'
        }
        # Only rename columns that exist and need renaming
        available_cols = df.columns.tolist()
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in available_cols})
    
    # Preview data
    print(f"\n Loading {csv_path}...")
    print(f"   Columns: {list(df.columns)}")
    print(f"   Rows: {len(df)}")
    
    
    
    # Load into database
    df.to_sql(table_name, conn, if_exists='append', index=False)
    
    print(f"    Loaded {len(df)} rows into '{table_name}' table.")
    return len(df)

def load_all_csv_data(conn):
    """
    Load all three domain CSV files into the database.
    """
    print("\n Starting CSV data loading...")
    
    total_rows = 0
    
    # Load cyber incidents
    total_rows += load_csv_to_table(
        conn,
        DATA_DIR / "cyber_incidents.csv",
        "cyber_incidents"
    )
    
    # Load datasets metadata
    total_rows += load_csv_to_table(
        conn,
        DATA_DIR / "datasets_metadata.csv",
        "datasets_metadata"
    )
    
    # Load IT tickets
    total_rows += load_csv_to_table(
        conn,
        DATA_DIR / "it_tickets.csv",
        "it_tickets"
    )
    
    print(f"\nTotal rows loaded: {total_rows}")
    return total_rows

