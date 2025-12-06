# CST1510 Coursework 2: Technical Report
## Multi-Domain Intelligence Platform

---

**Student Information:**
- **Full Name:** Nirav Prithviraj Ramsamy
- **Student ID:** M01067520
- **Module:** CST1510
- **Degree Program:** Computer Science

---

## Section 1: Introduction and Project Scope

### Project Goal

The Multi-Domain Intelligence Platform is a unified web application developed using Python and Streamlit, designed to serve three distinct user groups within an organization: Cybersecurity Analysts, Data Scientists, and IT Administrators. The platform addresses critical, real-world operational challenges by providing high-value analysis, actionable insights, and comprehensive data management capabilities tailored to each domain's specific needs.

The core objective of this project was to create a secure, scalable, and user-friendly platform that integrates modern software engineering practices including secure authentication, relational database management, object-oriented programming, interactive data visualization, and AI-powered assistance.

### Tiered Scope

This implementation achieves **Tier 3 (High Distinction)** by delivering complete, fully functional dashboards for all three domains:

1. **Cybersecurity Dashboard** - Incident response management and threat analysis
2. **Data Science Dashboard** - Dataset governance and resource management
3. **IT Operations Dashboard** - Service desk performance monitoring

Each domain includes complete CRUD functionality, interactive Plotly visualizations, high-value analytical insights, and an integrated AI assistant powered by Google Gemini API.

---

## Section 2: System Architecture and Implementation

### Data Layer and Security

#### Authentication Security

The platform implements secure user authentication using **bcrypt** password hashing with automatic salt generation. This approach ensures that:

- Passwords are never stored in plain text
- Each password hash includes a unique salt, preventing rainbow table attacks
- The bcrypt algorithm's computational cost makes brute-force attacks impractical

The authentication flow was initially implemented using file-based storage (`users.txt`) in Week 7, then migrated to SQLite in Week 8, demonstrating the evolution from simple persistence to proper database management.

```python
# Password hashing implementation (app/models/user.py)
def set_password(self, plain_password: str) -> None:
    salt = bcrypt.gensalt()
    self._password_hash = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
```

#### Database Design

The application uses **SQLite** as the relational database with a normalized schema comprising four primary tables:

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `users` | User authentication and roles | id, username, password_hash, role |
| `cyber_incidents` | Security incident tracking | id, date, incident_type, severity, status |
| `datasets_metadata` | Dataset catalog management | id, dataset_name, category, source, file_size_mb |
| `it_tickets` | IT support ticket tracking | id, ticket_id, priority, status, assigned_to |

All database queries use **parameterized statements** to prevent SQL injection vulnerabilities.

### Application Structure (MVC and Data Flow)

The application follows an MVC-inspired architecture adapted for Streamlit's reactive framework:

#### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE (View)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  Login.py   │  │  Cyber      │  │  DataSci    │  │  IT Ops     │ │
│  │             │  │  Dashboard  │  │  Dashboard  │  │  Dashboard  │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘ │
└─────────┼────────────────┼────────────────┼────────────────┼────────┘
          │                │                │                │
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      SERVICES (Controller)                           │
│  ┌─────────────────┐              ┌─────────────────────┐           │
│  │  user_service   │              │   gemini_service    │           │
│  │  (Auth Logic)   │              │   (AI Integration)  │           │
│  └────────┬────────┘              └──────────┬──────────┘           │
└───────────┼──────────────────────────────────┼──────────────────────┘
            │                                  │
            ▼                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER (Model)                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │  users   │  │ incidents│  │ datasets │  │ tickets  │            │
│  │  .py     │  │  .py     │  │  .py     │  │  .py     │            │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘            │
└───────┼─────────────┼─────────────┼─────────────┼───────────────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    SQLite DATABASE (db.py)                           │
│                  intelligence_platform.db                            │
└─────────────────────────────────────────────────────────────────────┘
```

**Data Flow Process:**
1. User interacts with Streamlit interface (View)
2. `st.session_state` manages authentication state across pages
3. Service layer handles business logic and external API calls
4. Data layer executes CRUD operations via parameterized SQL
5. Results flow back through the stack to update the UI

### Object-Oriented Programming (OOP) Design

#### UML Class Diagram

```
┌─────────────────────────────────────┐
│              User                    │
├─────────────────────────────────────┤
│ - _id: int                          │
│ - _username: str                    │
│ - _password_hash: str               │
│ - _role: str                        │
├─────────────────────────────────────┤
│ + set_password(plain: str)          │
│ + verify_password(plain: str): bool │
│ + has_access_to_domain(d: str): bool│
│ + save(): int                       │
│ + find_by_username(u: str): User    │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│         SecurityIncident            │
├─────────────────────────────────────┤
│ - _id: int                          │
│ - _incident_type: str               │
│ - _severity: str                    │
│ - _status: str                      │
├─────────────────────────────────────┤
│ + is_critical(): bool               │
│ + escalate(): void                  │
│ + resolve(): void                   │
│ + get_phishing_count(): int         │
│ + count_by_type(): dict             │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│             Dataset                  │
├─────────────────────────────────────┤
│ - _id: int                          │
│ - _dataset_name: str                │
│ - _file_size_mb: float              │
│ - _record_count: int                │
├─────────────────────────────────────┤
│ + is_large_dataset(): bool          │
│ + needs_archiving(): bool           │
│ + get_top_consumer(): tuple         │
│ + get_storage_by_source(): dict     │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│             ITTicket                 │
├─────────────────────────────────────┤
│ - _id: int                          │
│ - _ticket_id: str                   │
│ - _priority: str                    │
│ - _assigned_to: str                 │
├─────────────────────────────────────┤
│ + is_waiting(): bool                │
│ + get_resolution_time_days(): int   │
│ + get_worst_performer(): tuple      │
│ + get_staff_performance(): dict     │
└─────────────────────────────────────┘
```

The OOP refactoring significantly improved code organization by:
- **Encapsulation:** Private attributes with property accessors ensure data validation
- **Business Logic Centralization:** Methods like `is_critical()`, `needs_archiving()`, and `get_worst_performer()` encapsulate domain-specific logic
- **Reusability:** Class methods provide factory patterns for database queries
- **Maintainability:** Clear separation of concerns makes the codebase easier to extend

### Feature Integration

#### Interactive Visualizations

Each dashboard implements multiple Plotly visualizations:
- **Bar Charts:** Incident type distribution, ticket priority breakdown
- **Pie Charts:** Severity distribution, storage consumption by source
- **Metrics Cards:** Real-time KPIs (total incidents, resolution rates, storage usage)

#### AI Assistant Integration

The platform integrates Google Gemini API with domain-specific system prompts that:
- Restrict responses to relevant domain topics only
- Provide context-aware analysis based on current database state
- Offer actionable recommendations based on data patterns

---

## Section 3: High-Value Analysis and Insights

### Cybersecurity Domain

**Problem Statement:** The security team faces a surge in Phishing incidents, creating a growing backlog of high-severity unresolved cases.

**Analysis and Findings:**

The Cybersecurity Dashboard reveals critical insights through automated analysis:

1. **Phishing Spike Detection:** The system automatically flags when phishing incidents exceed 30% of total incidents as a "PHISHING SURGE"
2. **Response Bottleneck Identification:** Analysis identifies which threat category has the highest unresolved case count
3. **Severity-Based Prioritization:** Critical/High severity cases in the backlog are highlighted for immediate attention

**Actionable Recommendations:**
- Deploy additional phishing awareness training when surge detected
- Implement stricter email filtering rules
- Allocate additional resources when backlog exceeds threshold
- Prioritize investigation of critical/high severity cases

### Data Science Domain

**Problem Statement:** Managing a growing catalog of large datasets requiring quality checks and resource management.

**Analysis and Findings:**

1. **Storage Concentration Risk:** The system detects when a single source consumes >50% of total storage
2. **Source Dependency Analysis:** Identifies over-reliance on single data sources (>60% dependency flagged as risk)
3. **Large Dataset Identification:** Automatically flags datasets >50MB for compression consideration

**Actionable Recommendations:**
- Implement archiving policy for datasets not updated in 6+ months
- Review large datasets for partitioning opportunities
- Ensure GDPR compliance for Customer Data category datasets

### IT Operations Domain

**Problem Statement:** Slow resolution times with suspected staff performance anomaly and process inefficiencies.

**Analysis and Findings:**

1. **Staff Performance Anomaly Detection:** Identifies staff members with resolution rates significantly below team average
2. **"Waiting for User" Bottleneck:** Quantifies tickets stuck in waiting status as percentage of open tickets
3. **Workload Imbalance:** Detects when ticket distribution is significantly uneven across staff

**Actionable Recommendations:**
- Provide immediate support/training to underperforming staff
- Implement automated reminders for tickets waiting >24 hours
- Rebalance workload when distribution exceeds 2:1 ratio
- Escalate tickets waiting >3 days

---

## Section 4: Reflection and Conclusion

### Learning Reflection

This 5-week project provided invaluable hands-on experience with full-stack development concepts:

1. **Security Best Practices:** Understanding password hashing with bcrypt and the importance of salts fundamentally changed my approach to authentication
2. **Database Design:** Implementing CRUD operations with parameterized queries reinforced the importance of SQL injection prevention
3. **OOP Principles:** Refactoring procedural code into classes demonstrated the real-world benefits of encapsulation and code organization
4. **API Integration:** Working with the Gemini API taught practical skills in handling external services, error handling, and context-aware prompting

### Challenges

The most significant technical hurdles included:

1. **Session State Management:** Understanding Streamlit's reactive model and properly managing `st.session_state` for authentication persistence required careful debugging
2. **Role-Based Access Control:** Implementing proper access restrictions across multiple dashboards while maintaining a clean user experience
3. **AI Integration:** Crafting effective system prompts that restricted the AI to domain-specific responses while remaining helpful

These challenges were overcome through iterative testing, documentation review, and systematic debugging.

### Conclusion & Future Work

The Multi-Domain Intelligence Platform successfully addresses the core problems for all three user groups, providing:
- Secure, role-based authentication
- Comprehensive data management with full CRUD capabilities
- Actionable insights through automated analysis and visualization
- AI-powered assistance for domain-specific queries

**Future enhancements could include:**
1. **Time-Series Analysis:** Adding trend visualization over time to identify patterns
2. **Email Notifications:** Automated alerts when critical thresholds are exceeded
3. **Export Functionality:** PDF report generation for stakeholder presentations
4. **Multi-tenant Support:** Expanding to support multiple organizations

---

## Appendix

### Running Instructions

```bash
# 1. Clone the repository
git clone https://github.com/nramsamy4-beep/CW2_M01067520_CST1510.git
cd CW2_M01067520_CST1510

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize database with sample data
python load_data.py

# 4. Run the application
streamlit run app.py

# 5. Access at http://localhost:8501
```

### Environment Variables

```
GEMINI_API_KEY_CYBERSECURITY=your_key_here
GEMINI_API_KEY_DATASCIENCE=your_key_here
GEMINI_API_KEY_ITOPERATIONS=your_key_here
```

### Repository Structure

```
CW2_M01067520_CST1510/
├── app.py                    # Main entry point
├── pages/                    # Streamlit pages
│   ├── 1_Login.py
│   ├── 2_Cybersecurity_Dashboard.py
│   ├── 3_DataScience_Dashboard.py
│   └── 4_IT_Operations_Dashboard.py
├── app/
│   ├── models/              # OOP Entity Classes
│   ├── data/                # Database CRUD operations
│   └── services/            # Business logic & AI
├── DATA/                    # CSV files & SQLite DB
└── requirements.txt
```

---

**Word Count:** ~1,450 words

**GitHub Repository:** https://github.com/nramsamy4-beep/CW2_M01067520_CST1510

