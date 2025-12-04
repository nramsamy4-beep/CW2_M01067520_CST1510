"""
Dataset Entity Class - OOP Implementation.

This class represents dataset metadata in the platform,
encapsulating data governance and resource management logic.
"""

from datetime import datetime
from typing import Optional, List
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from app.data.db import connect_database


class Dataset:
    """
    Represents dataset metadata for data governance.
    
    Attributes:
        id (int): Unique identifier
        dataset_name (str): Name of the dataset
        category (str): Dataset category
        source (str): Data source/uploader
        last_updated (str): Last update date
        record_count (int): Number of records
        file_size_mb (float): File size in megabytes
    
    Example:
        >>> dataset = Dataset(
        ...     dataset_name="Customer_Data_2024",
        ...     category="Customer Data",
        ...     source="IT Department",
        ...     record_count=50000,
        ...     file_size_mb=125.5
        ... )
        >>> dataset.save()
    """
    
    VALID_CATEGORIES = ['General', 'Threat Intelligence', 'Network Logs', 'Customer Data']
    
    # Thresholds for data governance recommendations
    LARGE_DATASET_THRESHOLD_MB = 100.0
    LARGE_RECORD_THRESHOLD = 100000
    
    def __init__(self, id: int = None, dataset_name: str = "", category: str = "General",
                 source: str = "", last_updated: str = None, record_count: int = 0,
                 file_size_mb: float = 0.0, created_at: datetime = None):
        """
        Initialize a Dataset object.
        """
        self._id = id
        self._dataset_name = dataset_name
        self._category = category if category in self.VALID_CATEGORIES else 'General'
        self._source = source
        self._last_updated = last_updated or datetime.now().strftime('%Y-%m-%d')
        self._record_count = record_count
        self._file_size_mb = file_size_mb
        self._created_at = created_at or datetime.now()
    
    # ==================== PROPERTIES ====================
    
    @property
    def id(self) -> Optional[int]:
        return self._id
    
    @property
    def dataset_name(self) -> str:
        return self._dataset_name
    
    @dataset_name.setter
    def dataset_name(self, value: str):
        if not value:
            raise ValueError("Dataset name cannot be empty")
        self._dataset_name = value
    
    @property
    def category(self) -> str:
        return self._category
    
    @category.setter
    def category(self, value: str):
        if value not in self.VALID_CATEGORIES:
            raise ValueError(f"Invalid category. Must be one of: {self.VALID_CATEGORIES}")
        self._category = value
    
    @property
    def source(self) -> str:
        return self._source
    
    @source.setter
    def source(self, value: str):
        self._source = value
    
    @property
    def last_updated(self) -> str:
        return self._last_updated
    
    @property
    def record_count(self) -> int:
        return self._record_count
    
    @record_count.setter
    def record_count(self, value: int):
        if value < 0:
            raise ValueError("Record count cannot be negative")
        self._record_count = value
    
    @property
    def file_size_mb(self) -> float:
        return self._file_size_mb
    
    @file_size_mb.setter
    def file_size_mb(self, value: float):
        if value < 0:
            raise ValueError("File size cannot be negative")
        self._file_size_mb = value
    
    # ==================== BUSINESS LOGIC METHODS ====================
    
    def is_large_dataset(self) -> bool:
        """
        Check if dataset is considered large (needs archiving consideration).
        
        Returns:
            bool: True if dataset exceeds size thresholds
        """
        return (self._file_size_mb > self.LARGE_DATASET_THRESHOLD_MB or 
                self._record_count > self.LARGE_RECORD_THRESHOLD)
    
    def get_size_category(self) -> str:
        """
        Get human-readable size category.
        
        Returns:
            str: Size category (Small, Medium, Large)
        """
        if self._file_size_mb < 10:
            return "Small"
        elif self._file_size_mb < 100:
            return "Medium"
        else:
            return "Large"
    
    def calculate_storage_cost(self, cost_per_mb: float = 0.02) -> float:
        """
        Calculate estimated storage cost.
        
        Args:
            cost_per_mb: Cost per megabyte (default $0.02)
            
        Returns:
            float: Estimated monthly storage cost
        """
        return self._file_size_mb * cost_per_mb
    
    def needs_archiving(self, days_threshold: int = 180) -> bool:
        """
        Check if dataset should be archived based on last update date.
        
        Args:
            days_threshold: Days since last update to trigger archiving
            
        Returns:
            bool: True if dataset should be considered for archiving
        """
        try:
            last_update = datetime.strptime(self._last_updated, '%Y-%m-%d')
            days_since_update = (datetime.now() - last_update).days
            return days_since_update > days_threshold
        except:
            return False
    
    def get_governance_recommendation(self) -> str:
        """
        Get data governance recommendation for this dataset.
        
        Returns:
            str: Recommendation text
        """
        recommendations = []
        
        if self.is_large_dataset():
            recommendations.append("Consider compression or partitioning")
        
        if self.needs_archiving():
            recommendations.append("Review for archiving (not updated in 6+ months)")
        
        if self._category == "Customer Data":
            recommendations.append("Ensure GDPR/data protection compliance")
        
        if not recommendations:
            return "No immediate action required"
        
        return "; ".join(recommendations)
    
    # ==================== DATABASE OPERATIONS ====================
    
    def save(self) -> int:
        """Save the dataset to the database."""
        conn = connect_database()
        cursor = conn.cursor()
        
        if self._id is None:
            cursor.execute("""
                INSERT INTO datasets_metadata 
                (dataset_name, category, source, last_updated, record_count, file_size_mb)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self._dataset_name, self._category, self._source,
                  self._last_updated, self._record_count, self._file_size_mb))
            self._id = cursor.lastrowid
        else:
            cursor.execute("""
                UPDATE datasets_metadata 
                SET dataset_name = ?, category = ?, source = ?, last_updated = ?,
                    record_count = ?, file_size_mb = ?
                WHERE id = ?
            """, (self._dataset_name, self._category, self._source,
                  self._last_updated, self._record_count, self._file_size_mb, self._id))
        
        conn.commit()
        conn.close()
        return self._id
    
    def delete(self) -> bool:
        """Delete the dataset from the database."""
        if self._id is None:
            return False
        
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM datasets_metadata WHERE id = ?", (self._id,))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        
        if rows_affected > 0:
            self._id = None
            return True
        return False
    
    # ==================== CLASS METHODS ====================
    
    @classmethod
    def find_by_id(cls, dataset_id: int) -> Optional['Dataset']:
        """Find a dataset by ID."""
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM datasets_metadata WHERE id = ?", (dataset_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def get_all(cls) -> List['Dataset']:
        """Get all datasets."""
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM datasets_metadata")
        rows = cursor.fetchall()
        conn.close()
        
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def get_by_source(cls, source: str) -> List['Dataset']:
        """Get all datasets from a specific source."""
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM datasets_metadata WHERE source = ?", (source,))
        rows = cursor.fetchall()
        conn.close()
        
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def get_total_storage(cls) -> float:
        """Get total storage used by all datasets."""
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(file_size_mb) FROM datasets_metadata")
        result = cursor.fetchone()
        conn.close()
        
        return result[0] or 0.0
    
    @classmethod
    def get_storage_by_source(cls) -> dict:
        """
        Get storage consumption by source (key analytics).
        
        Returns:
            dict: source -> total_mb
        """
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT source, SUM(file_size_mb) as total_size
            FROM datasets_metadata
            GROUP BY source
            ORDER BY total_size DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        
        return {row[0]: row[1] for row in rows}
    
    @classmethod
    def get_top_consumer(cls) -> tuple:
        """
        Get the source consuming the most storage.
        
        Returns:
            tuple: (source_name, total_mb)
        """
        storage = cls.get_storage_by_source()
        if storage:
            top_source = max(storage, key=storage.get)
            return (top_source, storage[top_source])
        return (None, 0.0)
    
    @classmethod
    def _from_row(cls, row) -> 'Dataset':
        """Create a Dataset object from a database row."""
        return cls(
            id=row[0],
            dataset_name=row[1],
            category=row[2],
            source=row[3],
            last_updated=row[4],
            record_count=row[5] if len(row) > 5 else 0,
            file_size_mb=row[6] if len(row) > 6 else 0.0,
            created_at=row[7] if len(row) > 7 else None
        )
    
    # ==================== MAGIC METHODS ====================
    
    def __str__(self) -> str:
        return f"Dataset(id={self._id}, name='{self._dataset_name}', size={self._file_size_mb}MB)"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self._id,
            'dataset_name': self._dataset_name,
            'category': self._category,
            'source': self._source,
            'last_updated': self._last_updated,
            'record_count': self._record_count,
            'file_size_mb': self._file_size_mb
        }

