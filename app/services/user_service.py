"""User service - business logic for authentication."""
import bcrypt
from pathlib import Path
from app.data.db import connect_database
from app.data.users import get_user_by_username, insert_user


def register_user(username, password, role='user'):
    """Register new user with password hashing."""
    if get_user_by_username(username):
        return False, f"Username '{username}' already exists."
    
    password_hash = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    
    insert_user(username, password_hash, role)
    return True, f"User '{username}' registered successfully!"


def login_user(username, password):
    """Authenticate user."""
    user = get_user_by_username(username)
    if not user:
        return False, "User not found."
    
    stored_hash = user[2]
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        return True, f"Login successful! Welcome, {username}!"
    return False, "Incorrect password."


def migrate_users_from_file(filepath='DATA/users.txt'):
    """
    Migrate users from Week 7 users.txt to database.
    Format in users.txt: username,hashed_password
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        print(f"⚠️  File not found: {filepath}")
        print("   Creating sample users instead...")
        return create_sample_users()
    
    conn = connect_database()
    cursor = conn.cursor()
    migrated_count = 0
    skipped_count = 0
    
    print(f"📂 Reading users from: {filepath}")
    
    with open(filepath, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Parse the line: username,hashed_password
            parts = line.split(',')
            
            if len(parts) >= 2:
                username = parts[0].strip()
                password_hash = parts[1].strip()
                role = 'user'  # Default role for migrated users
                
                try:
                    # Try to insert the user
                    cursor.execute(
                        "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                        (username, password_hash, role)
                    )
                    
                    if cursor.rowcount > 0:
                        migrated_count += 1
                        print(f"   ✅ Migrated: {username}")
                    else:
                        skipped_count += 1
                        print(f"   ⏭️  Skipped (already exists): {username}")
                        
                except Exception as e:
                    print(f"   ❌ Error migrating {username}: {e}")
            else:
                print(f"   ⚠️  Line {line_num} has invalid format, skipping...")
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 Migration Summary:")
    print(f"   • Migrated: {migrated_count} users")
    print(f"   • Skipped: {skipped_count} users")
    print(f"   ✅ Total in database: {migrated_count + skipped_count}")
    
    return migrated_count


def create_sample_users():
    """Create sample users if users.txt doesn't exist."""
    sample_users = [
        ("admin", "admin123", "admin"),
        ("analyst1", "analyst123", "analyst"),
        ("user1", "user123", "user"),
    ]
    
    count = 0
    for username, password, role in sample_users:
        success, msg = register_user(username, password, role)
        if success:
            count += 1
            print(f"   ✅ Created: {username}")
    
    print(f"\n📊 Created {count} sample users")
    return count