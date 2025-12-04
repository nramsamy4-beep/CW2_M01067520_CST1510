"""Gemini API integration for domain-specific AI assistants."""
import os
import google.generativeai as genai
from typing import Optional, List
import pandas as pd


# Domain-specific API key environment variable names
API_KEY_CYBERSECURITY = "GEMINI_API_KEY_CYBERSECURITY"
API_KEY_DATASCIENCE = "GEMINI_API_KEY_DATASCIENCE"
API_KEY_ITOPERATIONS = "GEMINI_API_KEY_ITOPERATIONS"

# Default model - will be updated based on available models
DEFAULT_MODEL = "models/gemini-2.5-flash"


def get_api_key(domain: str) -> Optional[str]:
    """Get the API key for a specific domain."""
    key_mapping = {
        "cybersecurity": API_KEY_CYBERSECURITY,
        "datascience": API_KEY_DATASCIENCE,
        "itoperations": API_KEY_ITOPERATIONS
    }
    env_var = key_mapping.get(domain.lower())
    if env_var:
        return os.getenv(env_var)
    return None


def configure_gemini(api_key: str):
    """Configure the Gemini API with the provided key."""
    genai.configure(api_key=api_key)


def list_available_models(api_key: str) -> List[str]:
    """List all available models for the given API key."""
    try:
        configure_gemini(api_key)
        models = []
        for model in genai.list_models():
            # supported_generation_methods can be a list of strings or objects
            supported_methods = model.supported_generation_methods
            if 'generateContent' in supported_methods:
                models.append(model.name)
        return models
    except Exception as e:
        return [f"Error listing models: {str(e)}"]


def get_best_available_model(api_key: str) -> str:
    """Get the best available model for content generation."""
    # Use gemini-2.5-flash directly
    return "models/gemini-2.5-flash"


def dataframe_to_context(df: pd.DataFrame, max_rows: int = 50) -> str:
    """Convert DataFrame to a string context for the AI."""
    if df.empty:
        return "No data available in the database."
    
    # Limit rows for context
    if len(df) > max_rows:
        df_sample = df.head(max_rows)
        context = f"Showing {max_rows} of {len(df)} total records:\n\n"
    else:
        df_sample = df
        context = f"Total records: {len(df)}\n\n"
    
    context += df_sample.to_string(index=False)
    return context


def get_cybersecurity_system_prompt() -> str:
    """System prompt for Cybersecurity domain AI assistant."""
    return """You are a Cybersecurity AI Assistant specialized ONLY in analyzing security incidents and cyber threats.

YOUR ROLE:
- Analyze cybersecurity incidents from the provided database
- Identify threat patterns, trends, and security risks
- Provide recommendations for incident response and mitigation
- Help with security incident prioritization and analysis

STRICT RULES:
1. You can ONLY answer questions related to cybersecurity, security incidents, threats, and the incident data provided
2. You must NOT answer general questions unrelated to cybersecurity
3. You must NOT provide information about other domains (IT tickets, datasets, etc.)
4. If asked about non-cybersecurity topics, politely decline and redirect to cybersecurity topics
5. Base your analysis on the actual incident data provided in the context

When analyzing incidents, consider:
- Incident types (Phishing, Malware, DDoS, Ransomware, Data Breach, Insider Threat)
- Severity levels (Low, Medium, High, Critical)
- Status (Open, Investigating, Resolved, Closed)
- Patterns and trends in the data

Always be professional and provide actionable security insights."""


def get_datascience_system_prompt() -> str:
    """System prompt for Data Science domain AI assistant."""
    return """You are a Data Science AI Assistant specialized ONLY in dataset management and data governance.

YOUR ROLE:
- Analyze dataset metadata and resource consumption
- Provide data governance recommendations
- Help with data quality assessment and optimization
- Advise on data archiving and lifecycle policies

STRICT RULES:
1. You can ONLY answer questions related to data science, datasets, data governance, and the dataset metadata provided
2. You must NOT answer general questions unrelated to data management
3. You must NOT provide information about other domains (security incidents, IT tickets, etc.)
4. If asked about non-data-science topics, politely decline and redirect to data-related topics
5. Base your analysis on the actual dataset metadata provided in the context

When analyzing datasets, consider:
- Dataset names and categories
- Record counts and file sizes
- Data sources and upload dates
- Resource consumption patterns
- Data governance best practices

Always provide actionable data management insights."""


def get_itoperations_system_prompt() -> str:
    """System prompt for IT Operations domain AI assistant."""
    return """You are an IT Operations AI Assistant specialized ONLY in IT service desk and ticket management.

YOUR ROLE:
- Analyze IT support tickets and service desk performance
- Identify bottlenecks and performance issues
- Help with ticket prioritization and workload distribution
- Provide recommendations for improving IT service delivery

STRICT RULES:
1. You can ONLY answer questions related to IT operations, support tickets, service desk, and the ticket data provided
2. You must NOT answer general questions unrelated to IT operations
3. You must NOT provide information about other domains (security incidents, datasets, etc.)
4. If asked about non-IT-operations topics, politely decline and redirect to IT support topics
5. Base your analysis on the actual ticket data provided in the context

When analyzing tickets, consider:
- Ticket priorities (Low, Medium, High, Critical)
- Status (Open, In Progress, Waiting for User, Resolved)
- Categories (Hardware, Software, Network, Support)
- Staff assignment and workload
- Resolution patterns and bottlenecks

Always provide actionable IT service management insights."""


def query_cybersecurity_assistant(question: str, incidents_df: pd.DataFrame, api_key: str) -> str:
    """Query the Cybersecurity AI assistant."""
    try:
        configure_gemini(api_key)
        
        # Auto-detect best available model
        model_name = get_best_available_model(api_key)
        model = genai.GenerativeModel(model_name)
        
        # Build context with incident data
        data_context = dataframe_to_context(incidents_df)
        
        # Create the full prompt
        system_prompt = get_cybersecurity_system_prompt()
        full_prompt = f"""{system_prompt}

CURRENT INCIDENT DATABASE:
{data_context}

USER QUESTION: {question}

Provide a helpful, focused response based on the cybersecurity incident data above. If the question is not related to cybersecurity, politely explain that you can only assist with cybersecurity-related queries."""

        response = model.generate_content(full_prompt)
        return response.text
        
    except Exception as e:
        return f"Error communicating with AI: {str(e)}"


def query_datascience_assistant(question: str, datasets_df: pd.DataFrame, api_key: str) -> str:
    """Query the Data Science AI assistant."""
    try:
        configure_gemini(api_key)
        
        # Auto-detect best available model
        model_name = get_best_available_model(api_key)
        model = genai.GenerativeModel(model_name)
        
        # Build context with dataset data
        data_context = dataframe_to_context(datasets_df)
        
        # Create the full prompt
        system_prompt = get_datascience_system_prompt()
        full_prompt = f"""{system_prompt}

CURRENT DATASET CATALOG:
{data_context}

USER QUESTION: {question}

Provide a helpful, focused response based on the dataset metadata above. If the question is not related to data science or data management, politely explain that you can only assist with data-related queries."""

        response = model.generate_content(full_prompt)
        return response.text
        
    except Exception as e:
        return f"Error communicating with AI: {str(e)}"


def query_itoperations_assistant(question: str, tickets_df: pd.DataFrame, api_key: str) -> str:
    """Query the IT Operations AI assistant."""
    try:
        configure_gemini(api_key)
        
        # Auto-detect best available model
        model_name = get_best_available_model(api_key)
        model = genai.GenerativeModel(model_name)
        
        # Build context with ticket data
        data_context = dataframe_to_context(tickets_df)
        
        # Create the full prompt
        system_prompt = get_itoperations_system_prompt()
        full_prompt = f"""{system_prompt}

CURRENT IT TICKET DATABASE:
{data_context}

USER QUESTION: {question}

Provide a helpful, focused response based on the IT ticket data above. If the question is not related to IT operations or service desk, politely explain that you can only assist with IT operations-related queries."""

        response = model.generate_content(full_prompt)
        return response.text
        
    except Exception as e:
        return f"Error communicating with AI: {str(e)}"

