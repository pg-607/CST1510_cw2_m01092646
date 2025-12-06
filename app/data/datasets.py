import pandas as pd
from app.data.db import connect_database

def insert_dataset(dataset_name, category, source, last_updated, record_count, file_size_mb):
    """
    Insert a new dataset into the database.
    
    Args:
        dataset_name: Name of the dataset
        category: Dataset category
        source: Source/origin of dataset
        last_updated: Last update date (YYYY-MM-DD)
        record_count: Number of records in dataset
        file_size_mb: File size in MB
        
    Returns:
        int: ID of the newly inserted dataset
    """
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO datasets_metadata 
        (dataset_name, category, source, last_updated, record_count, file_size_mb)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (dataset_name, category, source, last_updated, record_count, file_size_mb))
    conn.commit()
    dataset_id = cursor.lastrowid
    conn.close()
    return dataset_id


def get_all_datasets():
    """Get all datasets as DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM datasets_metadata ORDER BY id DESC", conn)
    conn.close()
    return df


def get_datasets_by_category(conn, category):
    """
    Retrieve datasets filtered by category.
    
    Args:
        conn: Database connection
        category: Category to filter by
        
    Returns:
        pandas.DataFrame: Filtered datasets
    """
    query = "SELECT * FROM datasets_metadata WHERE category = ? ORDER BY id DESC"
    df = pd.read_sql_query(query, conn, params=(category,))
    return df


def get_datasets_by_source(conn, source):
    """
    Retrieve datasets filtered by source.
    
    Args:
        conn: Database connection
        source: Source to filter by
        
    Returns:
        pandas.DataFrame: Filtered datasets
    """
    query = "SELECT * FROM datasets_metadata WHERE source = ? ORDER BY id DESC"
    df = pd.read_sql_query(query, conn, params=(source,))
    return df


def update_dataset_category(conn, dataset_id, new_category):
    """
    Update the category of a dataset.
    
    Args:
        conn: Database connection
        dataset_id: ID of the dataset to update
        new_category: New category value
        
    Returns:
        bool: True if update was successful
    """
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE datasets_metadata SET category = ? WHERE id = ?",
        (new_category, dataset_id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    
    if rows_affected > 0:
        print(f"✓ Dataset #{dataset_id} category updated to '{new_category}'.")
        return True
    else:
        print(f"✗ No dataset found with ID {dataset_id}.")
        return False


def delete_dataset(conn, dataset_id):
    """
    Delete a dataset from the database.
    
    Args:
        conn: Database connection
        dataset_id: ID of the dataset to delete
        
    Returns:
        bool: True if deletion was successful
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM datasets_metadata WHERE id = ?", (dataset_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    
    if rows_affected > 0:
        print(f"✓ Dataset #{dataset_id} deleted successfully.")
        return True
    else:
        print(f"✗ No dataset found with ID {dataset_id}.")
        return False


def load_datasets_csv(csv_path):
    """
    Load datasets from CSV file into database.
    Use this if you have a custom CSV format.
    """
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
        df.to_sql('datasets_metadata', conn, if_exists='append', index=False)
        conn.close()
        
        print(f"  ✓ Loaded {len(df)} datasets")
        return len(df)
        
    except Exception as e:
        print(f"  ❌ Error loading CSV: {e}")
        return 0