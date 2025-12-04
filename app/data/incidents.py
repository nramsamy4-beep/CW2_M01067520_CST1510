"""Cyber incident CRUD operations."""
import pandas as pd
from app.data.db import connect_database


def insert_incident(date, incident_type, severity, status, description, reported_by=None):
    """Insert new incident."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cyber_incidents 
        (date, incident_type, severity, status, description, reported_by)
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


def get_incident_by_id(incident_id):
    """Get specific incident by ID."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents WHERE id = ?",
        conn,
        params=(incident_id,)
    )
    conn.close()
    return df


def update_incident_status(incident_id, new_status):
    """Update incident status."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE cyber_incidents SET status = ? WHERE id = ?",
        (new_status, incident_id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected


def delete_incident(incident_id):
    """Delete an incident."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cyber_incidents WHERE id = ?", (incident_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected


def get_incidents_by_type():
    """Count incidents by type."""
    conn = connect_database()
    df = pd.read_sql_query("""
        SELECT incident_type, COUNT(*) as count
        FROM cyber_incidents
        GROUP BY incident_type
        ORDER BY count DESC
    """, conn)
    conn.close()
    return df


def load_incidents_from_csv(csv_path):
    """Load incidents from CSV file matching YOUR CSV format."""
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
        # YOUR CSV: incident_id, timestamp, severity, category, status, description
        # DB needs: date, incident_type, severity, status, description, reported_by
        
        column_mapping = {
            'timestamp': 'date',           # timestamp → date
            'category': 'incident_type',   # category → incident_type
        }
        
        df.rename(columns=column_mapping, inplace=True)
        
        # Remove incident_id (database auto-generates id)
        if 'incident_id' in df.columns:
            df = df.drop('incident_id', axis=1)
        
        # Add missing required columns with defaults
        if 'reported_by' not in df.columns:
            df['reported_by'] = 'system'
        
        # Select only the columns we need
        final_columns = ['date', 'incident_type', 'severity', 'status', 'description', 'reported_by']
        df = df[final_columns]
        
        # Insert into database
        df.to_sql('cyber_incidents', conn, if_exists='append', index=False)
        conn.close()
        
        print(f"   ✅ Loaded {len(df)} incidents")
        return len(df)
        
    except Exception as e:
        print(f"   ❌ Error loading CSV: {e}")
        return 0
