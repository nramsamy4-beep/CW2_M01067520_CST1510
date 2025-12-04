"""
OOP Entity Classes for Multi-Domain Intelligence Platform.

This module contains the core entity classes that represent the data models
for the application, following Object-Oriented Programming principles.

Classes:
    - User: Represents a system user with authentication
    - SecurityIncident: Represents a cybersecurity incident
    - Dataset: Represents dataset metadata for data governance
    - ITTicket: Represents an IT support ticket
"""

from app.models.user import User
from app.models.security_incident import SecurityIncident
from app.models.dataset import Dataset
from app.models.it_ticket import ITTicket

__all__ = ['User', 'SecurityIncident', 'Dataset', 'ITTicket']

