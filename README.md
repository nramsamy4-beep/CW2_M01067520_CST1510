# Multi-Domain Intelligence Platform

A unified web application built with Python and Streamlit that serves three distinct user groups: **Cybersecurity Analysts**, **Data Scientists**, and **IT Administrators**.

## 🎯 Project Overview

This platform addresses specific, real-world problems within each domain:

| Domain | Core Problem | Solution |
|--------|-------------|----------|
| 🛡️ **Cybersecurity** | Incident Response Bottleneck & Phishing Surge | Threat trend analysis, backlog identification, and actionable security recommendations |
| 📈 **Data Science** | Data Governance & Resource Management | Storage consumption analysis, source dependency tracking, and archiving policies |
| 🖥️ **IT Operations** | Service Desk Performance | Staff performance anomaly detection, process bottleneck analysis |

## 🏗️ System Architecture

### Technology Stack
- **Frontend:** Streamlit (Multi-page application)
- **Backend:** Python 3.x
- **Database:** SQLite
- **Authentication:** bcrypt password hashing
- **AI Integration:** Google Gemini API
- **Visualization:** Plotly

### Project Structure
```
├── app.py                      # Main application entry point
├── pages/                      # Streamlit pages
│   ├── 1_Login.py             # Authentication page
│   ├── 2_Cybersecurity_Dashboard.py
│   ├── 3_DataScience_Dashboard.py
│   └── 4_IT_Operations_Dashboard.py
├── app/
│   ├── models/                 # OOP Entity Classes
│   │   ├── user.py            # User class
│   │   ├── security_incident.py
│   │   ├── dataset.py
│   │   └── it_ticket.py
│   ├── data/                   # Database operations
│   │   ├── db.py              # Database connection
│   │   ├── schema.py          # Table definitions
│   │   ├── users.py           # User CRUD
│   │   ├── incidents.py       # Incident CRUD
│   │   ├── datasets.py        # Dataset CRUD
│   │   └── tickets.py         # Ticket CRUD
│   └── services/
│       ├── user_service.py    # Authentication service
│       └── gemini_service.py  # AI integration
├── DATA/                       # CSV data files
└── requirements.txt
```

## 🔐 Security Features

- **Password Hashing:** bcrypt with automatic salt generation
- **Role-Based Access Control (RBAC):**
  - `security_analyst` → Cybersecurity Dashboard
  - `data_scientist` → Data Science Dashboard
  - `it_admin` → IT Operations Dashboard
  - `admin` → All Dashboards

## 🧠 OOP Design

The application uses Object-Oriented Programming with four core entity classes:

### User Class
```python
user = User(username="john", role="security_analyst")
user.set_password("secure123")
user.save()
user.has_access_to_domain("cybersecurity")  # True
```

### SecurityIncident Class
```python
incident = SecurityIncident(incident_type="Phishing", severity="High")
incident.is_critical()  # True
incident.escalate()     # Increase severity
SecurityIncident.get_phishing_count()  # Analytics
```

### Dataset Class
```python
dataset = Dataset(dataset_name="Customer_Data", file_size_mb=125.5)
dataset.is_large_dataset()  # Check archiving need
Dataset.get_top_consumer()  # Storage analytics
```

### ITTicket Class
```python
ticket = ITTicket(ticket_id="TKT001", priority="High")
ticket.is_waiting()  # Bottleneck indicator
ITTicket.get_worst_performer()  # Staff analytics
```

## 🤖 AI Integration

Each domain has a dedicated AI assistant powered by Google Gemini:

- **Cybersecurity AI:** Security incident analysis and threat recommendations
- **Data Science AI:** Data governance advice and resource optimization
- **IT Operations AI:** Service desk performance insights

### Configuration
Set your Gemini API keys as environment variables:
```bash
GEMINI_API_KEY_CYBERSECURITY=your_key_here
GEMINI_API_KEY_DATASCIENCE=your_key_here
GEMINI_API_KEY_ITOPERATIONS=your_key_here
```

Or enter them directly in the dashboard's "API Configuration" section.

## 📊 High-Value Insights

### Cybersecurity Domain
- Phishing spike detection and trend analysis
- Incident response backlog identification
- Severity-based prioritization recommendations

### Data Science Domain
- Storage consumption by source analysis
- Data source dependency risk assessment
- GDPR compliance recommendations for customer data

### IT Operations Domain
- Staff performance anomaly detection
- "Waiting for User" bottleneck analysis
- Workload distribution recommendations

## 🚀 Installation & Running

### Prerequisites
- Python 3.8+
- pip package manager

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd edit-CW2_M01067520_CST1510

# Install dependencies
pip install -r requirements.txt

# Initialize database (optional - loads sample data)
python load_data.py

# Run the application
streamlit run app.py
```

### Default Access
Navigate to `http://localhost:8501` and register a new account with your desired role.

## 📈 Visualizations

Each dashboard includes:
- **Bar Charts:** Distribution analysis (threat types, priorities, categories)
- **Pie Charts:** Proportional breakdowns (severity, status, storage)
- **Metrics Cards:** Key performance indicators
- **Data Tables:** Detailed record views with filtering

## 🔄 CRUD Operations

All domains support full CRUD functionality:
- **Create:** Add new records via forms
- **Read:** View filtered data tables
- **Update:** Modify record status/properties
- **Delete:** Remove records with confirmation

## 📝 Report Requirements

This project fulfills the following assessment criteria:

1. ✅ **Secure Authentication** (bcrypt hashing)
2. ✅ **Database Design** (SQLite with normalized schema)
3. ✅ **OOP Refactoring** (Entity classes with business logic)
4. ✅ **Multi-Page Streamlit Application**
5. ✅ **Interactive Visualizations** (Plotly)
6. ✅ **AI Assistant Integration** (Gemini API)
7. ✅ **Role-Based Access Control**
8. ✅ **High-Value Insights & Recommendations**

## 👤 Author

**Student ID:** M01067520  
**Module:** CST1510  
**Tier:** 3 (All Three Domains)

## 📄 License

This project is submitted as coursework for CST1510.

