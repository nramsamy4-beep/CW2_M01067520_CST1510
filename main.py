"""
Main demo script for Week 8 Database Implementation
Student ID: M01067520
"""

from pathlib import Path
from app.data.db import connect_database
from app.data.schema import create_all_tables
from app.services.user_service import register_user, login_user, migrate_users_from_file
from app.data.incidents import (
    insert_incident, 
    get_all_incidents, 
    update_incident_status,
    get_incidents_by_type,
    load_incidents_from_csv
)
from app.data.datasets import load_datasets_from_csv
from app.data.tickets import load_tickets_from_csv


def main():
    print("=" * 60)
    print("🚀 Week 8: Database Demo - M01067520")
    print("=" * 60)
    
    # 1. Setup database
    print("\n[1] Setting up database...")
    conn = connect_database()
    create_all_tables(conn)
    conn.close()
    
    # 2. Migrate/create users
    print("\n[2] Setting up users...")
    migrate_users_from_file()
    
    # 3. Load CSV data if available
    print("\n[3] Loading CSV data...")
    data_dir = Path("DATA")
    
    # Load incidents
    incidents_csv = data_dir / "cyber_incidents.csv"
    if incidents_csv.exists():
        count = load_incidents_from_csv(incidents_csv)
        print(f"   ✅ Loaded {count} incidents")
    else:
        print(f"   ⚠️  {incidents_csv} not found")
    
    # Load datasets
    datasets_csv = data_dir / "datasets_metadata.csv"
    if datasets_csv.exists():
        count = load_datasets_from_csv(datasets_csv)
        print(f"   ✅ Loaded {count} datasets")
    else:
        print(f"   ⚠️  {datasets_csv} not found")
    
    # Load tickets
    tickets_csv = data_dir / "it_tickets.csv"
    if tickets_csv.exists():
        count = load_tickets_from_csv(tickets_csv)
        print(f"   ✅ Loaded {count} tickets")
    else:
        print(f"   ⚠️  {tickets_csv} not found")
    
    # 4. Test authentication
    print("\n[4] Testing authentication...")
    success, msg = register_user("test_user", "TestPass123!", "user")
    print(f"   Register: {msg}")
    
    success, msg = login_user("test_user", "TestPass123!")
    print(f"   Login: {msg}")
    
    # 5. Test CRUD
    print("\n[5] Testing CRUD operations...")
    incident_id = insert_incident(
        "2024-12-02",
        "Phishing",
        "High",
        "Open",
        "Suspicious email detected - testing database",
        "test_user"
    )
    print(f"   ✅ Created incident #{incident_id}")
    
    # Update
    update_incident_status(incident_id, "Investigating")
    print(f"   ✅ Updated incident #{incident_id} status")
    
    # 6. Query data
    print("\n[6] Querying database...")
    df = get_all_incidents()
    print(f"   📊 Total incidents in database: {len(df)}")
    
    df_by_type = get_incidents_by_type()
    print(f"   📊 Unique incident types: {len(df_by_type)}")
    if len(df_by_type) > 0:
        print("\n   Top 3 incident types:")
        for idx, row in df_by_type.head(3).iterrows():
            print(f"      - {row['incident_type']}: {row['count']}")
    
    print("\n" + "=" * 60)
    print("✅ Demo completed successfully!")
    print("=" * 60)
    print(f"\n📁 Database location: {Path('DATA/intelligence_platform.db').resolve()}")
    print("\n💡 You can now:")
    print("   - Use DB Browser to view your database")
    print("   - Continue to Week 9 (Streamlit interface)")
    print("   - Run tests and add more data")


if __name__ == "__main__":
    main()