"""IT ticket CRUD operations."""
import pandas as pd
from app.data.db import connect_database


def get_all_tickets():
    """Get all tickets as DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM it_tickets ORDER BY id DESC", conn)
    conn.close()
    return df


def load_tickets_from_csv(csv_path):
    """Load tickets from CSV file matching YOUR CSV format."""
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
        # YOUR CSV: ticket_id, priority, description, status, assigned_to, created_at, resolution_time_hours
        # DB needs: ticket_id, priority, status, category, subject, description, created_date, resolved_date, assigned_to
        
        column_mapping = {
            'created_at': 'created_date',   # created_at → created_date
        }
        
        df.rename(columns=column_mapping, inplace=True)
        
        # Add missing required columns with defaults
        if 'subject' not in df.columns:
            # Use first 50 chars of description as subject
            df['subject'] = df['description'].str[:50]
        
        if 'category' not in df.columns:
            df['category'] = 'General'
        
        if 'resolved_date' not in df.columns:
            df['resolved_date'] = None
        
        # Remove columns not in database
        if 'resolution_time_hours' in df.columns:
            df = df.drop('resolution_time_hours', axis=1)
        
        # Select final columns
        final_columns = ['ticket_id', 'priority', 'status', 'category', 'subject', 
                        'description', 'created_date', 'resolved_date', 'assigned_to']
        df = df[final_columns]
        
        # Insert into database
        df.to_sql('it_tickets', conn, if_exists='append', index=False)
        conn.close()
        
        print(f"   ✅ Loaded {len(df)} tickets")
        return len(df)
        
    except Exception as e:
        print(f"   ❌ Error loading CSV: {e}")
        return 0


def insert_ticket(ticket_id, priority, status, category, subject, description, assigned_to, created_date):
    """Insert new ticket."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO it_tickets 
        (ticket_id, priority, status, category, subject, description, created_date, assigned_to)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (ticket_id, priority, status, category, subject, description, created_date, assigned_to))
    conn.commit()
    ticket_db_id = cursor.lastrowid
    conn.close()
    return ticket_db_id


def update_ticket_status(ticket_id, new_status):
    """Update ticket status."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE it_tickets SET status = ? WHERE ticket_id = ?",
        (new_status, ticket_id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected


def delete_ticket(ticket_id):
    """Delete a ticket."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM it_tickets WHERE ticket_id = ?", (ticket_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected