import pandas as pd
from pathlib import Path
from app.data.db import connect_database
from app.data.schema import create_all_tables
from app.services.user_service import register_user, login_user, migrate_users_from_file
from app.data.incidents import (
    insert_incident, get_all_incidents, get_incidents_by_severity,
    update_incident_status, delete_incident, get_incidents_by_type_count
)
from app.data.datasets import get_all_datasets, get_total_storage_by_format
from app.data.tickets import get_all_tickets, get_tickets_by_category_count


def load_csv_data(conn):
    """
    Load CSV files into database tables.
    
    Args:
        conn: Database connection
    """
    print("\n" + "="*60)
    print("LOADING CSV DATA")
    print("="*60)
    
    DATA_DIR = Path("DATA")
    
    # Load cyber incidents
    csv_path = DATA_DIR / "cyber_incidents.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        df.to_sql('cyber_incidents', conn, if_exists='append', index=False)
        print(f"✅ Loaded {len(df)} cyber incidents")
    else:
        print(f"⚠️ {csv_path} not found")
    
    # Load datasets metadata
    csv_path = DATA_DIR / "datasets_metadata.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        df.to_sql('datasets_metadata', conn, if_exists='append', index=False)
        print(f"✅ Loaded {len(df)} datasets")
    else:
        print(f"⚠️ {csv_path} not found")
    
    # Load IT tickets
    csv_path = DATA_DIR / "it_tickets.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        df.to_sql('it_tickets', conn, if_exists='append', index=False)
        print(f"✅ Loaded {len(df)} IT tickets")
    else:
        print(f"⚠️ {csv_path} not found")


def demo_authentication():
    """Demonstrate user authentication functionality."""
    print("\n" + "="*60)
    print("🔐 AUTHENTICATION DEMO")
    print("="*60)
    
    # Register new users
    print("\n[1] Registering new users...")
    success, msg = register_user("alice", "SecurePass123!", "analyst")
    print(f"  {'✅' if success else '❌'} {msg}")
    
    success, msg = register_user("bob", "BobPass456!", "user")
    print(f"  {'✅' if success else '❌'} {msg}")
    
    # Test login
    print("\n[2] Testing login...")
    success, msg = login_user("alice", "SecurePass123!")
    print(f"  {'✅' if success else '❌'} {msg}")
    
    success, msg = login_user("alice", "WrongPassword")
    print(f"  {'✅' if success else '❌'} {msg}")


def demo_crud_operations():
    """Demonstrate CRUD operations on incidents."""
    print("\n" + "="*60)
    print("CRUD OPERATIONS DEMO")
    print("="*60)
    
    # CREATE
    print("\n[1] CREATE - Inserting new incident...")
    incident_id = insert_incident(
        date="2024-11-05",
        incident_type="Phishing",
        severity="High",
        status="Open",
        description="Suspicious email with malicious link detected",
        reported_by="alice"
    )
    
    # READ
    print("\n[2] READ - Querying incidents...")
    df_all = get_all_incidents()
    print(f"  Total incidents in database: {len(df_all)}")
    
    df_high = get_incidents_by_severity("High")
    print(f"  High severity incidents: {len(df_high)}")
    
    # UPDATE
    print("\n[3] UPDATE - Updating incident status...")
    update_incident_status(incident_id, "Investigating")
    
    # DELETE (commented out for safety)
    print("\n[4] DELETE - Delete functionality available")
    print("  (Skipped in demo to preserve data)")
    # delete_incident(incident_id)


def demo_analytical_queries():
    """Demonstrate analytical SQL queries."""
    print("\n" + "="*60)
    print("📊 ANALYTICAL QUERIES DEMO")
    print("="*60)
    
    # Incidents by type
    print("\n[1] Incidents by Type:")
    df_by_type = get_incidents_by_type_count()
    print(df_by_type.to_string(index=False))
    
    # Storage by format
    print("\n[2] Dataset Storage by Format:")
    df_storage = get_total_storage_by_format()
    print(df_storage.to_string(index=False))
    
    # Tickets by category
    print("\n[3] IT Tickets by Category:")
    df_tickets = get_tickets_by_category_count()
    print(df_tickets.to_string(index=False))


def display_database_summary():
    """Display summary of database contents."""
    print("\n" + "="*60)
    print("DATABASE SUMMARY")
    print("="*60)
    
    conn = connect_database()
    cursor = conn.cursor()
    
    tables = ['users', 'cyber_incidents', 'datasets_metadata', 'it_tickets']
    
    print(f"\n{'Table':<25} {'Row Count':<15}")
    print("-" * 40)
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table:<25} {count:<15}")
    
    conn.close()


def main():
    """Main execution function."""
    print("="*60)
    print("DATABASE DEMO")
    print("   Multi-Domain Intelligence Platform")
    print("="*60)
    
    # Ensure DATA directory exists
    Path("DATA").mkdir(parents=True, exist_ok=True)
    
    # Step 1: Setup database
    print("\n[STEP 1/6] Setting up database...")
    conn = connect_database()
    create_all_tables(conn)
    conn.close()
    
    # Step 2: Migrate users
    print("\n[STEP 2/6] Migrating users from text file...")
    migrate_users_from_file()
    
    # Step 3: Load CSV data
    print("\n[STEP 3/6] Loading CSV data...")
    conn = connect_database()
    try:
        load_csv_data(conn)
    except Exception as e:
        print(f"⚠️ Note: {e}")
        print("  (CSV files may not exist yet - this is OK for initial setup)")
    finally:
        conn.close()
    
    # Step 4: Demo authentication
    print("\n[STEP 4/6] Demonstrating authentication...")
    demo_authentication()
    
    # Step 5: Demo CRUD operations
    print("\n[STEP 5/6] Demonstrating CRUD operations...")
    demo_crud_operations()
    
    # Step 6: Demo analytical queries
    print("\n[STEP 6/6] Demonstrating analytical queries...")
    try:
        demo_analytical_queries()
    except Exception as e:
        print(f"⚠️ Note: Some queries may fail if CSV data wasn't loaded")
    
    # Final summary
    display_database_summary()
    
    # Success message
    print("\n" + "="*60)
    print("✅ DATABASE SETUP AND DEMO COMPLETE!")
    print("="*60)
    print("\n" + "="*60)


if __name__ == "__main__":
    main()