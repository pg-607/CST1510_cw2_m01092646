import pandas as pd
from .db import connect_database

def insert_incident(date, incident_type, severity, status, description, reported_by=None):
    """Insert new incident."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cyber_incidents
        (timestamp, category, severity, status, description, reported_by)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (date, incident_type, severity, status, description, reported_by))
    conn.commit()
    incident_id = cursor.lastrowid
    conn.close()
    return incident_id

def get_all_incidents():
    """Get all incidents as DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents ORDER BY id DESC",
        conn
    )
    conn.close()
    return df

def get_incidents_by_severity(conn, severity):
    """
    Retrieve incidents filtered by severity.
    
    Args:
        conn: Database connection
        severity: Severity level to filter by
        
    Returns:
        pandas.DataFrame: Filtered incidents
    """
    query = "SELECT * FROM cyber_incidents WHERE severity = ? ORDER BY id DESC"
    df = pd.read_sql_query(query, conn, params=(severity,))
    return df

def get_incidents_by_status(conn, status):
    """
    Retrieve incidents filtered by status.
    
    Args:
        conn: Database connection
        status: Status to filter by
        
    Returns:
        pandas.DataFrame: Filtered incidents
    """
    query = "SELECT * FROM cyber_incidents WHERE status = ? ORDER BY id DESC"
    df = pd.read_sql_query(query, conn, params=(status,))
    return df

def update_incident_status(conn, incident_id, new_status):
    """
    Update the status of an incident.
    
    Args:
        conn: Database connection
        incident_id: ID of the incident to update
        new_status: New status value
        
    Returns:
        bool: True if update was successful
    """
    cursor = conn.cursor()
    
    # Use parameterized query
    cursor.execute(
        "UPDATE cyber_incidents SET status = ? WHERE id = ?",
        (new_status, incident_id)
    )
    
    conn.commit()
    rows_affected = cursor.rowcount
    
    if rows_affected > 0:
        print(f"[OK] Incident #{incident_id} status updated to '{new_status}'.")
        return True
    else:
        print(f"[ERROR] No incident found with ID {incident_id}.")
        return False

def delete_incident(conn, incident_id):
    """
    Delete an incident from the database.
    
    Args:
        conn: Database connection
        incident_id: ID of the incident to delete
        
    Returns:
        bool: True if deletion was successful
    """
    cursor = conn.cursor()
    
    # CRITICAL: Always use WHERE clause with DELETE!
    cursor.execute(
        "DELETE FROM cyber_incidents WHERE id = ?",
        (incident_id,)
    )
    
    conn.commit()
    rows_affected = cursor.rowcount
    
    if rows_affected > 0:
        print(f"[OK] Incident #{incident_id} deleted successfully.")
        return True
    else:
        print(f"[ERROR] No incident found with ID {incident_id}.")
        return False
    
def get_incidents_by_type_count(conn):
    """
    Count incidents by type.
    Uses: SELECT, FROM, GROUP BY, ORDER BY
    """
    query = """
    SELECT category, COUNT(*) as count
    FROM cyber_incidents
    GROUP BY category
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_high_severity_by_status(conn):
    """
    Count high severity incidents by status.
    Uses: SELECT, FROM, WHERE, GROUP BY, ORDER BY
    """
    query = """
    SELECT status, COUNT(*) as count
    FROM cyber_incidents
    WHERE severity = 'High'
    GROUP BY status
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_incident_types_with_many_cases(conn, min_count=5):
    """
    Find incident types with more than min_count cases.
    Uses: SELECT, FROM, GROUP BY, HAVING, ORDER BY
    """
    query = """
    SELECT incident_type, COUNT(*) as count
    FROM cyber_incidents
    GROUP BY incident_type
    HAVING COUNT(*) > ?
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn, params=(min_count,))
    return df