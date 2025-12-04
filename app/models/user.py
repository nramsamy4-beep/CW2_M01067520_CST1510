"""
User Entity Class - OOP Implementation.

This class represents a user in the Multi-Domain Intelligence Platform,
encapsulating user data and authentication-related business logic.
"""

import bcrypt
from datetime import datetime
from typing import Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from app.data.db import connect_database


class User:
    """
    Represents a system user with authentication capabilities.
    
    Attributes:
        id (int): Unique identifier for the user
        username (str): User's login name
        password_hash (str): Bcrypt hashed password
        role (str): User's role (security_analyst, data_scientist, it_admin, admin)
        created_at (datetime): Account creation timestamp
    
    Example:
        >>> user = User(username="john_doe", role="security_analyst")
        >>> user.set_password("secure_password123")
        >>> user.save()
    """
    
    # Valid roles in the system
    VALID_ROLES = ['security_analyst', 'data_scientist', 'it_admin', 'admin']
    
    def __init__(self, id: int = None, username: str = "", password_hash: str = "", 
                 role: str = "security_analyst", created_at: datetime = None):
        """
        Initialize a User object.
        
        Args:
            id: Database ID (None for new users)
            username: User's login name
            password_hash: Bcrypt hashed password
            role: User's role in the system
            created_at: Account creation timestamp
        """
        self._id = id
        self._username = username
        self._password_hash = password_hash
        self._role = role if role in self.VALID_ROLES else 'security_analyst'
        self._created_at = created_at or datetime.now()
    
    # ==================== PROPERTIES (Getters/Setters) ====================
    
    @property
    def id(self) -> Optional[int]:
        """Get user ID."""
        return self._id
    
    @property
    def username(self) -> str:
        """Get username."""
        return self._username
    
    @username.setter
    def username(self, value: str):
        """Set username with validation."""
        if not value or len(value) < 3:
            raise ValueError("Username must be at least 3 characters long")
        self._username = value
    
    @property
    def role(self) -> str:
        """Get user role."""
        return self._role
    
    @role.setter
    def role(self, value: str):
        """Set role with validation."""
        if value not in self.VALID_ROLES:
            raise ValueError(f"Invalid role. Must be one of: {self.VALID_ROLES}")
        self._role = value
    
    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._created_at
    
    # ==================== BUSINESS LOGIC METHODS ====================
    
    def set_password(self, plain_password: str) -> None:
        """
        Hash and set the user's password using bcrypt.
        
        Args:
            plain_password: The plain text password to hash
        """
        if len(plain_password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        
        salt = bcrypt.gensalt()
        self._password_hash = bcrypt.hashpw(plain_password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, plain_password: str) -> bool:
        """
        Verify a password against the stored hash.
        
        Args:
            plain_password: The plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        if not self._password_hash:
            return False
        return bcrypt.checkpw(plain_password.encode('utf-8'), self._password_hash.encode('utf-8'))
    
    def has_access_to_domain(self, domain: str) -> bool:
        """
        Check if user has access to a specific domain.
        
        Args:
            domain: The domain to check ('cybersecurity', 'datascience', 'itoperations')
            
        Returns:
            bool: True if user has access, False otherwise
        """
        # Admin has access to all domains
        if self._role == 'admin':
            return True
        
        # Map roles to domains
        role_domain_map = {
            'security_analyst': 'cybersecurity',
            'data_scientist': 'datascience',
            'it_admin': 'itoperations'
        }
        
        return role_domain_map.get(self._role) == domain.lower()
    
    def get_role_display_name(self) -> str:
        """
        Get a human-readable display name for the user's role.
        
        Returns:
            str: Formatted role name with emoji
        """
        role_display = {
            'security_analyst': '🛡️ Security Analyst',
            'data_scientist': '📈 Data Scientist',
            'it_admin': '🖥️ IT Administrator',
            'admin': '👑 Admin'
        }
        return role_display.get(self._role, self._role)
    
    # ==================== DATABASE OPERATIONS ====================
    
    def save(self) -> int:
        """
        Save the user to the database (insert or update).
        
        Returns:
            int: The user's ID after saving
        """
        conn = connect_database()
        cursor = conn.cursor()
        
        if self._id is None:
            # Insert new user
            cursor.execute("""
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            """, (self._username, self._password_hash, self._role))
            self._id = cursor.lastrowid
        else:
            # Update existing user
            cursor.execute("""
                UPDATE users SET username = ?, password_hash = ?, role = ?
                WHERE id = ?
            """, (self._username, self._password_hash, self._role, self._id))
        
        conn.commit()
        conn.close()
        return self._id
    
    def delete(self) -> bool:
        """
        Delete the user from the database.
        
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        if self._id is None:
            return False
        
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (self._id,))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        
        if rows_affected > 0:
            self._id = None
            return True
        return False
    
    # ==================== CLASS METHODS (Factory Methods) ====================
    
    @classmethod
    def find_by_id(cls, user_id: int) -> Optional['User']:
        """
        Find a user by their ID.
        
        Args:
            user_id: The user's database ID
            
        Returns:
            User object if found, None otherwise
        """
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return cls(
                id=row[0],
                username=row[1],
                password_hash=row[2],
                role=row[3],
                created_at=row[4] if len(row) > 4 else None
            )
        return None
    
    @classmethod
    def find_by_username(cls, username: str) -> Optional['User']:
        """
        Find a user by their username.
        
        Args:
            username: The user's login name
            
        Returns:
            User object if found, None otherwise
        """
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return cls(
                id=row[0],
                username=row[1],
                password_hash=row[2],
                role=row[3],
                created_at=row[4] if len(row) > 4 else None
            )
        return None
    
    @classmethod
    def get_all(cls) -> list:
        """
        Get all users from the database.
        
        Returns:
            List of User objects
        """
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        conn.close()
        
        return [cls(
            id=row[0],
            username=row[1],
            password_hash=row[2],
            role=row[3],
            created_at=row[4] if len(row) > 4 else None
        ) for row in rows]
    
    # ==================== MAGIC METHODS ====================
    
    def __str__(self) -> str:
        """String representation of the user."""
        return f"User(id={self._id}, username='{self._username}', role='{self._role}')"
    
    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return self.__str__()
    
    def to_dict(self) -> dict:
        """
        Convert user to dictionary (for JSON serialization).
        
        Returns:
            dict: User data as dictionary
        """
        return {
            'id': self._id,
            'username': self._username,
            'role': self._role,
            'created_at': str(self._created_at) if self._created_at else None
        }

