"""
SecurityIncident Entity Class - OOP Implementation.

This class represents a cybersecurity incident in the platform,
encapsulating incident data and security analysis business logic.
"""

from datetime import datetime
from typing import Optional, List
import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from app.data.db import connect_database


class SecurityIncident:
    """
    Represents a cybersecurity incident.
    
    Attributes:
        id (int): Unique identifier
        date (str): Date of the incident
        incident_type (str): Type of threat (Phishing, Malware, etc.)
        severity (str): Severity level (Low, Medium, High, Critical)
        status (str): Current status (Open, Investigating, Resolved, Closed)
        description (str): Detailed description of the incident
        reported_by (str): Username of reporter
    
    Example:
        >>> incident = SecurityIncident(
        ...     incident_type="Phishing",
        ...     severity="High",
        ...     description="Suspicious email targeting finance department"
        ... )
        >>> incident.save()
    """
    
    # Valid values for incident attributes
    VALID_TYPES = ['Phishing', 'Malware', 'DDoS', 'Ransomware', 'Data Breach', 'Insider Threat']
    VALID_SEVERITIES = ['Low', 'Medium', 'High', 'Critical']
    VALID_STATUSES = ['Open', 'Investigating', 'Resolved', 'Closed']
    
    def __init__(self, id: int = None, date: str = None, incident_type: str = "Phishing",
                 severity: str = "Medium", status: str = "Open", description: str = "",
                 reported_by: str = None, created_at: datetime = None):
        """
        Initialize a SecurityIncident object.
        
        Args:
            id: Database ID (None for new incidents)
            date: Date of the incident
            incident_type: Type of threat
            severity: Severity level
            status: Current status
            description: Incident description
            reported_by: Username of reporter
            created_at: Creation timestamp
        """
        self._id = id
        self._date = date or datetime.now().strftime('%Y-%m-%d')
        self._incident_type = incident_type if incident_type in self.VALID_TYPES else 'Phishing'
        self._severity = severity if severity in self.VALID_SEVERITIES else 'Medium'
        self._status = status if status in self.VALID_STATUSES else 'Open'
        self._description = description
        self._reported_by = reported_by
        self._created_at = created_at or datetime.now()
    
    # ==================== PROPERTIES ====================
    
    @property
    def id(self) -> Optional[int]:
        return self._id
    
    @property
    def date(self) -> str:
        return self._date
    
    @date.setter
    def date(self, value: str):
        self._date = value
    
    @property
    def incident_type(self) -> str:
        return self._incident_type
    
    @incident_type.setter
    def incident_type(self, value: str):
        if value not in self.VALID_TYPES:
            raise ValueError(f"Invalid incident type. Must be one of: {self.VALID_TYPES}")
        self._incident_type = value
    
    @property
    def severity(self) -> str:
        return self._severity
    
    @severity.setter
    def severity(self, value: str):
        if value not in self.VALID_SEVERITIES:
            raise ValueError(f"Invalid severity. Must be one of: {self.VALID_SEVERITIES}")
        self._severity = value
    
    @property
    def status(self) -> str:
        return self._status
    
    @status.setter
    def status(self, value: str):
        if value not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {self.VALID_STATUSES}")
        self._status = value
    
    @property
    def description(self) -> str:
        return self._description
    
    @description.setter
    def description(self, value: str):
        self._description = value
    
    @property
    def reported_by(self) -> Optional[str]:
        return self._reported_by
    
    # ==================== BUSINESS LOGIC METHODS ====================
    
    def is_critical(self) -> bool:
        """
        Check if the incident is critical priority.
        
        Returns:
            bool: True if severity is Critical or High
        """
        return self._severity in ['Critical', 'High']
    
    def is_open(self) -> bool:
        """
        Check if the incident is still open.
        
        Returns:
            bool: True if status is Open or Investigating
        """
        return self._status in ['Open', 'Investigating']
    
    def resolve(self) -> None:
        """Mark the incident as resolved."""
        self._status = 'Resolved'
    
    def close(self) -> None:
        """Mark the incident as closed."""
        self._status = 'Closed'
    
    def escalate(self) -> None:
        """Escalate the incident to the next severity level."""
        severity_order = ['Low', 'Medium', 'High', 'Critical']
        current_index = severity_order.index(self._severity)
        if current_index < len(severity_order) - 1:
            self._severity = severity_order[current_index + 1]
    
    def get_severity_color(self) -> str:
        """
        Get a color code for the severity level (for UI display).
        
        Returns:
            str: Color name for the severity
        """
        colors = {
            'Low': 'green',
            'Medium': 'yellow',
            'High': 'orange',
            'Critical': 'red'
        }
        return colors.get(self._severity, 'gray')
    
    # ==================== DATABASE OPERATIONS ====================
    
    def save(self) -> int:
        """
        Save the incident to the database.
        
        Returns:
            int: The incident's ID after saving
        """
        conn = connect_database()
        cursor = conn.cursor()
        
        if self._id is None:
            cursor.execute("""
                INSERT INTO cyber_incidents 
                (date, incident_type, severity, status, description, reported_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self._date, self._incident_type, self._severity, 
                  self._status, self._description, self._reported_by))
            self._id = cursor.lastrowid
        else:
            cursor.execute("""
                UPDATE cyber_incidents 
                SET date = ?, incident_type = ?, severity = ?, status = ?, 
                    description = ?, reported_by = ?
                WHERE id = ?
            """, (self._date, self._incident_type, self._severity,
                  self._status, self._description, self._reported_by, self._id))
        
        conn.commit()
        conn.close()
        return self._id
    
    def delete(self) -> bool:
        """Delete the incident from the database."""
        if self._id is None:
            return False
        
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cyber_incidents WHERE id = ?", (self._id,))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        
        if rows_affected > 0:
            self._id = None
            return True
        return False
    
    # ==================== CLASS METHODS ====================
    
    @classmethod
    def find_by_id(cls, incident_id: int) -> Optional['SecurityIncident']:
        """Find an incident by ID."""
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cyber_incidents WHERE id = ?", (incident_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def get_all(cls) -> List['SecurityIncident']:
        """Get all incidents."""
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cyber_incidents ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def get_by_type(cls, incident_type: str) -> List['SecurityIncident']:
        """Get all incidents of a specific type."""
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM cyber_incidents WHERE incident_type = ? ORDER BY id DESC",
            (incident_type,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def get_open_incidents(cls) -> List['SecurityIncident']:
        """Get all open/investigating incidents."""
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM cyber_incidents WHERE status IN ('Open', 'Investigating') ORDER BY id DESC"
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def get_critical_incidents(cls) -> List['SecurityIncident']:
        """Get all critical/high severity incidents."""
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM cyber_incidents WHERE severity IN ('Critical', 'High') ORDER BY id DESC"
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def count_by_type(cls) -> dict:
        """
        Count incidents by type (for analytics).
        
        Returns:
            dict: Dictionary of incident_type -> count
        """
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT incident_type, COUNT(*) as count
            FROM cyber_incidents
            GROUP BY incident_type
        """)
        rows = cursor.fetchall()
        conn.close()
        
        return {row[0]: row[1] for row in rows}
    
    @classmethod
    def get_phishing_count(cls) -> int:
        """Get count of phishing incidents (key metric)."""
        counts = cls.count_by_type()
        return counts.get('Phishing', 0)
    
    @classmethod
    def _from_row(cls, row) -> 'SecurityIncident':
        """Create an incident object from a database row."""
        return cls(
            id=row[0],
            date=row[1],
            incident_type=row[2],
            severity=row[3],
            status=row[4],
            description=row[5] if len(row) > 5 else "",
            reported_by=row[6] if len(row) > 6 else None,
            created_at=row[7] if len(row) > 7 else None
        )
    
    # ==================== MAGIC METHODS ====================
    
    def __str__(self) -> str:
        return f"SecurityIncident(id={self._id}, type='{self._incident_type}', severity='{self._severity}', status='{self._status}')"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self._id,
            'date': self._date,
            'incident_type': self._incident_type,
            'severity': self._severity,
            'status': self._status,
            'description': self._description,
            'reported_by': self._reported_by
        }

