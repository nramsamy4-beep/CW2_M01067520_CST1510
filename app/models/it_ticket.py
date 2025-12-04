"""
ITTicket Entity Class - OOP Implementation.

This class represents an IT support ticket in the platform,
encapsulating ticket data and service desk performance logic.
"""

from datetime import datetime
from typing import Optional, List
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from app.data.db import connect_database


class ITTicket:
    """
    Represents an IT support ticket.
    
    Attributes:
        id (int): Database ID
        ticket_id (str): Ticket reference number
        priority (str): Priority level (Low, Medium, High, Critical)
        status (str): Current status
        category (str): Ticket category
        subject (str): Ticket subject
        description (str): Detailed description
        assigned_to (str): Staff member assigned
        created_date (str): Creation date
        resolved_date (str): Resolution date
    
    Example:
        >>> ticket = ITTicket(
        ...     ticket_id="TKT20241204001",
        ...     priority="High",
        ...     subject="Network connectivity issue",
        ...     assigned_to="IT_Support_A"
        ... )
        >>> ticket.save()
    """
    
    VALID_PRIORITIES = ['Low', 'Medium', 'High', 'Critical']
    VALID_STATUSES = ['Open', 'In Progress', 'Waiting for User', 'Resolved']
    VALID_CATEGORIES = ['Hardware', 'Software', 'Network', 'Support']
    
    def __init__(self, id: int = None, ticket_id: str = "", priority: str = "Medium",
                 status: str = "Open", category: str = "Support", subject: str = "",
                 description: str = "", assigned_to: str = "", created_date: str = None,
                 resolved_date: str = None, created_at: datetime = None):
        """
        Initialize an ITTicket object.
        """
        self._id = id
        self._ticket_id = ticket_id
        self._priority = priority if priority in self.VALID_PRIORITIES else 'Medium'
        self._status = status if status in self.VALID_STATUSES else 'Open'
        self._category = category if category in self.VALID_CATEGORIES else 'Support'
        self._subject = subject
        self._description = description
        self._assigned_to = assigned_to
        self._created_date = created_date or datetime.now().strftime('%Y-%m-%d')
        self._resolved_date = resolved_date
        self._created_at = created_at or datetime.now()
    
    # ==================== PROPERTIES ====================
    
    @property
    def id(self) -> Optional[int]:
        return self._id
    
    @property
    def ticket_id(self) -> str:
        return self._ticket_id
    
    @ticket_id.setter
    def ticket_id(self, value: str):
        self._ticket_id = value
    
    @property
    def priority(self) -> str:
        return self._priority
    
    @priority.setter
    def priority(self, value: str):
        if value not in self.VALID_PRIORITIES:
            raise ValueError(f"Invalid priority. Must be one of: {self.VALID_PRIORITIES}")
        self._priority = value
    
    @property
    def status(self) -> str:
        return self._status
    
    @status.setter
    def status(self, value: str):
        if value not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {self.VALID_STATUSES}")
        self._status = value
    
    @property
    def category(self) -> str:
        return self._category
    
    @property
    def subject(self) -> str:
        return self._subject
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def assigned_to(self) -> str:
        return self._assigned_to
    
    @assigned_to.setter
    def assigned_to(self, value: str):
        self._assigned_to = value
    
    @property
    def created_date(self) -> str:
        return self._created_date
    
    @property
    def resolved_date(self) -> Optional[str]:
        return self._resolved_date
    
    # ==================== BUSINESS LOGIC METHODS ====================
    
    def is_high_priority(self) -> bool:
        """Check if ticket is high priority."""
        return self._priority in ['High', 'Critical']
    
    def is_open(self) -> bool:
        """Check if ticket is still open."""
        return self._status in ['Open', 'In Progress', 'Waiting for User']
    
    def is_waiting(self) -> bool:
        """Check if ticket is in 'Waiting for User' status (bottleneck indicator)."""
        return self._status == 'Waiting for User'
    
    def resolve(self) -> None:
        """Mark the ticket as resolved and set resolution date."""
        self._status = 'Resolved'
        self._resolved_date = datetime.now().strftime('%Y-%m-%d')
    
    def escalate(self) -> None:
        """Escalate ticket priority."""
        priority_order = ['Low', 'Medium', 'High', 'Critical']
        current_index = priority_order.index(self._priority)
        if current_index < len(priority_order) - 1:
            self._priority = priority_order[current_index + 1]
    
    def reassign(self, new_assignee: str) -> None:
        """Reassign ticket to another staff member."""
        self._assigned_to = new_assignee
    
    def get_resolution_time_days(self) -> Optional[int]:
        """
        Calculate resolution time in days.
        
        Returns:
            int: Days to resolve, or None if not resolved
        """
        if not self._resolved_date:
            return None
        
        try:
            created = datetime.strptime(self._created_date, '%Y-%m-%d')
            resolved = datetime.strptime(self._resolved_date, '%Y-%m-%d')
            return (resolved - created).days
        except:
            return None
    
    def get_age_days(self) -> int:
        """
        Get ticket age in days.
        
        Returns:
            int: Days since ticket was created
        """
        try:
            created = datetime.strptime(self._created_date, '%Y-%m-%d')
            return (datetime.now() - created).days
        except:
            return 0
    
    def get_priority_color(self) -> str:
        """Get color code for priority level."""
        colors = {
            'Low': 'green',
            'Medium': 'blue',
            'High': 'orange',
            'Critical': 'red'
        }
        return colors.get(self._priority, 'gray')
    
    # ==================== DATABASE OPERATIONS ====================
    
    def save(self) -> int:
        """Save the ticket to the database."""
        conn = connect_database()
        cursor = conn.cursor()
        
        if self._id is None:
            cursor.execute("""
                INSERT INTO it_tickets 
                (ticket_id, priority, status, category, subject, description, 
                 created_date, resolved_date, assigned_to)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (self._ticket_id, self._priority, self._status, self._category,
                  self._subject, self._description, self._created_date,
                  self._resolved_date, self._assigned_to))
            self._id = cursor.lastrowid
        else:
            cursor.execute("""
                UPDATE it_tickets 
                SET ticket_id = ?, priority = ?, status = ?, category = ?,
                    subject = ?, description = ?, created_date = ?,
                    resolved_date = ?, assigned_to = ?
                WHERE id = ?
            """, (self._ticket_id, self._priority, self._status, self._category,
                  self._subject, self._description, self._created_date,
                  self._resolved_date, self._assigned_to, self._id))
        
        conn.commit()
        conn.close()
        return self._id
    
    def delete(self) -> bool:
        """Delete the ticket from the database."""
        if self._id is None:
            return False
        
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM it_tickets WHERE id = ?", (self._id,))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        
        if rows_affected > 0:
            self._id = None
            return True
        return False
    
    # ==================== CLASS METHODS ====================
    
    @classmethod
    def find_by_id(cls, db_id: int) -> Optional['ITTicket']:
        """Find a ticket by database ID."""
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM it_tickets WHERE id = ?", (db_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def find_by_ticket_id(cls, ticket_id: str) -> Optional['ITTicket']:
        """Find a ticket by ticket reference number."""
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM it_tickets WHERE ticket_id = ?", (ticket_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def get_all(cls) -> List['ITTicket']:
        """Get all tickets."""
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM it_tickets ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def get_by_assignee(cls, assignee: str) -> List['ITTicket']:
        """Get all tickets assigned to a specific staff member."""
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM it_tickets WHERE assigned_to = ? ORDER BY id DESC",
            (assignee,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def get_waiting_tickets(cls) -> List['ITTicket']:
        """Get all tickets in 'Waiting for User' status."""
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM it_tickets WHERE status = 'Waiting for User' ORDER BY id DESC"
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def get_staff_performance(cls) -> dict:
        """
        Calculate staff performance metrics.
        
        Returns:
            dict: Staff -> {total, resolved, resolution_rate}
        """
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                assigned_to,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) as resolved
            FROM it_tickets
            GROUP BY assigned_to
        """)
        rows = cursor.fetchall()
        conn.close()
        
        performance = {}
        for row in rows:
            staff = row[0]
            total = row[1]
            resolved = row[2]
            rate = (resolved / total * 100) if total > 0 else 0
            performance[staff] = {
                'total': total,
                'resolved': resolved,
                'resolution_rate': round(rate, 2)
            }
        
        return performance
    
    @classmethod
    def get_worst_performer(cls) -> tuple:
        """
        Identify staff member with lowest resolution rate.
        
        Returns:
            tuple: (staff_name, resolution_rate)
        """
        performance = cls.get_staff_performance()
        if not performance:
            return (None, 0)
        
        worst = min(performance, key=lambda x: performance[x]['resolution_rate'])
        return (worst, performance[worst]['resolution_rate'])
    
    @classmethod
    def count_waiting_tickets(cls) -> int:
        """Count tickets in 'Waiting for User' status."""
        return len(cls.get_waiting_tickets())
    
    @classmethod
    def _from_row(cls, row) -> 'ITTicket':
        """Create an ITTicket object from a database row."""
        return cls(
            id=row[0],
            ticket_id=row[1],
            priority=row[2],
            status=row[3],
            category=row[4],
            subject=row[5],
            description=row[6] if len(row) > 6 else "",
            created_date=row[7] if len(row) > 7 else None,
            resolved_date=row[8] if len(row) > 8 else None,
            assigned_to=row[9] if len(row) > 9 else "",
            created_at=row[10] if len(row) > 10 else None
        )
    
    # ==================== MAGIC METHODS ====================
    
    def __str__(self) -> str:
        return f"ITTicket(id={self._ticket_id}, priority='{self._priority}', status='{self._status}', assigned='{self._assigned_to}')"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self._id,
            'ticket_id': self._ticket_id,
            'priority': self._priority,
            'status': self._status,
            'category': self._category,
            'subject': self._subject,
            'description': self._description,
            'assigned_to': self._assigned_to,
            'created_date': self._created_date,
            'resolved_date': self._resolved_date
        }

