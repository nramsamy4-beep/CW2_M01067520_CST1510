"""Load CSV data into the database."""
from pathlib import Path
import pandas as pd
from app.data.db import connect_database
from app.data.schema import create_all_tables
from app.data.incidents import load_incidents_from_csv

def load_all_csv_data():
    """Load all CSV files into database."""
    print("\n" + "="*60)
    print("LOADING CSV DATA INTO DATABASE")
    print("="*60)
    
    # Create tables first
    conn = connect_database()
    create_all_tables(conn)
    conn.close()
    print("✅ Tables created")
    
    # Define CSV paths
    DATA_DIR = Path("DATA")
    
    # Load cyber incidents
    print("\n📊 Loading Cyber Incidents...")
    incidents_loaded = load_incidents_from_csv(DATA_DIR / "cyber_incidents.csv")
    
    # Load datasets metadata
    print("\n📊 Loading Datasets Metadata...")
    try:
        conn = connect_database()
        df = pd.read_csv(DATA_DIR / "datasets_metadata.csv")
        
        # Map CSV columns to database columns
        # CSV has: dataset_id, name, rows, columns, uploaded_by, upload_date
        # DB needs: dataset_name, category, source, last_updated, record_count, file_size_mb
        
        df_mapped = pd.DataFrame({
            'dataset_name': df['name'],
            'category': 'General',  # Default category
            'source': df['uploaded_by'],
            'last_updated': df['upload_date'],
            'record_count': df['rows'],
            'file_size_mb': (df['rows'] * df['columns'] * 0.001)  # Estimate file size
        })
        
        df_mapped.to_sql('datasets_metadata', conn, if_exists='append', index=False)
        conn.close()
        print(f"   ✅ Loaded {len(df_mapped)} datasets")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Load IT tickets
    print("\n📊 Loading IT Tickets...")
    try:
        conn = connect_database()
        df = pd.read_csv(DATA_DIR / "it_tickets.csv")
        
        # Map CSV columns to database columns
        # CSV has: ticket_id, priority, description, status, assigned_to, created_at, resolution_time_hours
        # DB needs: ticket_id, priority, status, category, subject, description, created_date, resolved_date, assigned_to
        
        df_mapped = pd.DataFrame({
            'ticket_id': df['ticket_id'].astype(str),
            'priority': df['priority'],
            'status': df['status'],
            'category': 'Support',  # Default category
            'subject': 'Ticket ' + df['ticket_id'].astype(str),
            'description': df['description'],
            'created_date': df['created_at'],
            'resolved_date': None,  # We don't have this in CSV
            'assigned_to': df['assigned_to']
        })
        
        df_mapped.to_sql('it_tickets', conn, if_exists='append', index=False)
        conn.close()
        print(f"   ✅ Loaded {len(df_mapped)} tickets")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*60)
    print("✅ DATA LOADING COMPLETE!")
    print("="*60)
    
    # Show summary
    print("\n📊 Database Summary:")
    conn = connect_database()
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM cyber_incidents")
    incidents_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM datasets_metadata")
    datasets_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM it_tickets")
    tickets_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"   🛡️  Cyber Incidents: {incidents_count}")
    print(f"   📈 Datasets: {datasets_count}")
    print(f"   🖥️  IT Tickets: {tickets_count}")
    print()

if __name__ == "__main__":
    load_all_csv_data()