import pandas as pd
from app.data.db import connect_database


def insert_ticket(priority, status, category, subject, description, created_date, resolved_date=None, assigned_to=None):
    """
    Insert a new IT ticket into the database.
    
    Args:
        priority: Ticket priority (High, Medium, Low)
        status: Ticket status (Open, In Progress, Resolved, Closed)
        category: Ticket category (Hardware, Software, Network, etc.)
        subject: Brief subject/title
        description: Detailed description
        created_date: When ticket was created (YYYY-MM-DD)
        resolved_date: When ticket was resolved (optional)
        assigned_to: Who it's assigned to (optional)
        
    Returns:
        int: ID of the newly inserted ticket
    """
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO it_tickets 
        (priority, status, category, subject, description, created_date, resolved_date, assigned_to)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (priority, status, category, subject, description, created_date, resolved_date, assigned_to))
    conn.commit()
    ticket_id = cursor.lastrowid
    conn.close()
    return ticket_id


def get_all_tickets():
    """Get all tickets as DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM it_tickets ORDER BY id DESC", conn)
    conn.close()
    return df


def get_tickets_by_status(conn, status):
    """Get tickets by status."""
    query = "SELECT * FROM it_tickets WHERE status = ? ORDER BY id DESC"
    df = pd.read_sql_query(query, conn, params=(status,))
    return df


def get_tickets_by_priority(conn, priority):
    """Get tickets by priority."""
    query = "SELECT * FROM it_tickets WHERE priority = ? ORDER BY id DESC"
    df = pd.read_sql_query(query, conn, params=(priority,))
    return df


def update_ticket_status(conn, ticket_id, new_status):
    """
    Update the status of a ticket.
    
    Args:
        conn: Database connection
        ticket_id: ID of the ticket to update
        new_status: New status value
        
    Returns:
        bool: True if update was successful
    """
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE it_tickets SET status = ? WHERE id = ?",
        (new_status, ticket_id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    
    if rows_affected > 0:
        print(f"✓ Ticket #{ticket_id} status updated to '{new_status}'.")
        return True
    else:
        print(f"✗ No ticket found with ID {ticket_id}.")
        return False


def delete_ticket(conn, ticket_id):
    """
    Delete a ticket from the database.
    
    Args:
        conn: Database connection
        ticket_id: ID of the ticket to delete
        
    Returns:
        bool: True if deletion was successful
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM it_tickets WHERE id = ?", (ticket_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    
    if rows_affected > 0:
        print(f"✓ Ticket #{ticket_id} deleted successfully.")
        return True
    else:
        print(f"✗ No ticket found with ID {ticket_id}.")
        return False


def load_tickets_from_csv(csv_path):
    """Load tickets from CSV file into database."""
    from pathlib import Path
    
    csv_path = Path(csv_path)
    if not csv_path.exists():
        print(f"⚠️ CSV file not found: {csv_path}")
        return 0
    
    try:
        conn = connect_database()
        df = pd.read_csv(csv_path)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        print(f"Loading {csv_path.name}...")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Rows: {len(df)}")
        
        # Load into database
        df.to_sql('it_tickets', conn, if_exists='append', index=False)
        conn.close()
        
        print(f"  ✓ Loaded {len(df)} tickets")
        return len(df)
        
    except Exception as e:
        print(f"  ❌ Error loading CSV: {e}")
        return 0