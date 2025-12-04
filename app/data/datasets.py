"""Dataset metadata CRUD operations."""
import pandas as pd
from app.data.db import connect_database


def get_all_datasets():
    """Get all datasets as DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM datasets_metadata", conn)
    conn.close()
    return df


def load_datasets_from_csv(csv_path):
    """Load datasets from CSV file matching YOUR CSV format."""
    from pathlib import Path
    
    csv_path = Path(csv_path)
    if not csv_path.exists():
        print(f"   ⚠️  CSV file not found: {csv_path}")
        return 0
    
    try:
        conn = connect_database()
        df = pd.read_csv(csv_path)
        
        print(f"   📄 CSV columns found: {list(df.columns)}")
        
        # Map YOUR CSV columns to database columns
        # YOUR CSV: dataset_id, name, rows, columns, uploaded_by, upload_date
        # DB needs: dataset_name, category, source, last_updated, record_count, file_size_mb
        
        column_mapping = {
            'name': 'dataset_name',         # name → dataset_name
            'uploaded_by': 'source',        # uploaded_by → source
            'upload_date': 'last_updated',  # upload_date → last_updated
            'rows': 'record_count',         # rows → record_count
        }
        
        df.rename(columns=column_mapping, inplace=True)
        
        # Remove dataset_id (database auto-generates id)
        if 'dataset_id' in df.columns:
            df = df.drop('dataset_id', axis=1)
        
        # Remove 'columns' column (not in our database)
        if 'columns' in df.columns:
            df = df.drop('columns', axis=1)
        
        # Add missing columns with defaults
        if 'category' not in df.columns:
            df['category'] = 'General'
        if 'file_size_mb' not in df.columns:
            df['file_size_mb'] = 0.0
        
        # Select final columns
        final_columns = ['dataset_name', 'category', 'source', 'last_updated', 'record_count', 'file_size_mb']
        df = df[final_columns]
        
        # Insert into database
        df.to_sql('datasets_metadata', conn, if_exists='append', index=False)
        conn.close()
        
        print(f"   ✅ Loaded {len(df)} datasets")
        return len(df)
        
    except Exception as e:
        print(f"   ❌ Error loading CSV: {e}")
        return 0
def insert_dataset(dataset_name, category, source, last_updated, record_count, file_size_mb):
    """Insert new dataset."""
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


def update_dataset_status(dataset_id, category):
    """Update dataset category."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE datasets_metadata SET category = ? WHERE id = ?",
        (category, dataset_id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected


def delete_dataset(dataset_id):
    """Delete a dataset."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM datasets_metadata WHERE id = ?", (dataset_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected