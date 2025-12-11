"""
Gemini API Integration for Multi-Domain Intelligence Platform.
Following Week 10 Lab structure with secure key storage and streaming support.

Student ID: M01067520
"""

import os
import time
from pathlib import Path
import google.generativeai as genai
from typing import Optional, List, Generator
import pandas as pd
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env file
# Try to load from project root directory
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)
# Also try current directory
load_dotenv()

# ============================================================
# API KEY MANAGEMENT (Secure - Following Week 10 Lab)
# ============================================================

# Fallback API key for examiners (works out of the box)
# Examiners can override this by setting GEMINI_API_KEY in .env file
EXAMINER_API_KEY = "AIzaSyCbk2qV2J-7Attvby1OkEJJKPBRyCpgcVQ"

# Fallback demo API keys for examiners (can be overridden via .env or Streamlit secrets)
FALLBACK_API_KEYS = {
    "cybersecurity": os.getenv("DEMO_GEMINI_KEY", EXAMINER_API_KEY),
    "datascience": os.getenv("DEMO_GEMINI_KEY", EXAMINER_API_KEY),
    "itoperations": os.getenv("DEMO_GEMINI_KEY", EXAMINER_API_KEY),
    "default": os.getenv("DEMO_GEMINI_KEY", EXAMINER_API_KEY)
}

def get_api_key(domain: str = "default") -> Optional[str]:
    """
    Get API key from environment variables or Streamlit secrets.
    Priority: st.secrets > os.environ > .env file > fallback demo key
    
    This function ensures examiners can use the AI assistant by:
    1. Checking Streamlit secrets (for deployment)
    2. Checking environment variables (.env file)
    3. Using fallback demo key if available
    
    Args:
        domain: 'cybersecurity', 'datascience', 'itoperations', or 'default'
    
    Returns:
        API key string or None
    """
    # Domain-specific key names
    key_names = {
        "cybersecurity": "GEMINI_API_KEY_CYBERSECURITY",
        "datascience": "GEMINI_API_KEY_DATASCIENCE", 
        "itoperations": "GEMINI_API_KEY_ITOPERATIONS",
        "default": "GEMINI_API_KEY"
    }
    
    key_name = key_names.get(domain.lower(), "GEMINI_API_KEY")
    
    # Priority 1: Try Streamlit secrets first (for deployment)
    try:
        if key_name in st.secrets:
            return st.secrets[key_name]
    except:
        pass
    
    # Priority 2: Fall back to environment variable
    api_key = os.getenv(key_name)
    
    # Priority 3: If domain-specific key not found, try default
    if not api_key and domain != "default":
        api_key = os.getenv("GEMINI_API_KEY")
        try:
            if "GEMINI_API_KEY" in st.secrets:
                api_key = st.secrets["GEMINI_API_KEY"]
        except:
            pass
    
    # Priority 4: Use fallback demo key if available (for examiners)
    if not api_key:
        fallback_key = FALLBACK_API_KEYS.get(domain.lower(), FALLBACK_API_KEYS["default"])
        if fallback_key and fallback_key.strip():
            return fallback_key
    
    return api_key


def configure_gemini(api_key: str) -> None:
    """Configure the Gemini API with the provided key."""
    genai.configure(api_key=api_key)


# ============================================================
# MODEL CONFIGURATION
# ============================================================

# Available Gemini models
AVAILABLE_MODELS = [
    "gemini-2.5-flash",  # Latest model (2.5 Flash)
    "gemini-1.5-flash",  # Stable option with good quotas
    "gemini-1.5-pro",
    "gemini-2.0-flash",
]

DEFAULT_MODEL = "gemini-2.5-flash"  # Using 2.5 Flash as requested


def list_available_models(api_key: str) -> List[str]:
    """List all available Gemini models."""
    try:
        configure_gemini(api_key)
        models = []
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                models.append(model.name)
        return models
    except Exception as e:
        return [f"Error: {str(e)}"]


def get_generation_config(temperature: float = 0.7, max_tokens: int = 2048) -> dict:
    """
    Get generation configuration (similar to OpenAI's parameters).
    
    Args:
        temperature: Controls randomness (0.0 = deterministic, 2.0 = very random)
        max_tokens: Maximum response length
    """
    return {
        "temperature": temperature,
        "max_output_tokens": max_tokens,
        "top_p": 0.95,
        "top_k": 40,
    }


# ============================================================
# DOMAIN-SPECIFIC SYSTEM PROMPTS
# ============================================================

SYSTEM_PROMPTS = {
    "cybersecurity": """You are a Cybersecurity AI Assistant specialized ONLY in analyzing security incidents and cyber threats.

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

Always be professional and provide actionable security insights.""",

    "datascience": """You are a Data Science AI Assistant specialized ONLY in dataset management and data governance.

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

Always provide actionable data management insights.""",

    "itoperations": """You are an IT Operations AI Assistant specialized ONLY in IT service desk and ticket management.

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
}


# ============================================================
# DATA CONTEXT HELPERS
# ============================================================

def dataframe_to_context(df: pd.DataFrame, max_rows: int = 50) -> str:
    """Convert DataFrame to string context for AI analysis."""
    if df is None or df.empty:
        return "No data available in the database."
    
    if len(df) > max_rows:
        context = f"Showing {max_rows} of {len(df)} total records:\n\n"
        df_sample = df.head(max_rows)
    else:
        context = f"Total records: {len(df)}\n\n"
        df_sample = df
    
    context += df_sample.to_string(index=False)
    return context


# ============================================================
# CHAT FUNCTIONS (Following Week 10 Lab Structure)
# ============================================================

def query_gemini(
    question: str,
    system_prompt: str,
    data_context: str,
    api_key: str,
    model_name: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    stream: bool = False
) -> str | Generator:
    """
    Query Gemini API (similar to OpenAI's chat.completions.create).
    
    Args:
        question: User's question
        system_prompt: Domain-specific system instructions
        data_context: Database data as context
        api_key: Gemini API key
        model_name: Model to use
        temperature: Response randomness (0.0-2.0)
        stream: Enable streaming response
    
    Returns:
        Response text or generator for streaming
    """
    try:
        configure_gemini(api_key)
        
        # Create the model with generation config
        generation_config = get_generation_config(temperature=temperature)
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config
        )
        
        # Build the full prompt (Gemini doesn't have separate system/user roles like OpenAI)
        full_prompt = f"""{system_prompt}

CURRENT DATABASE CONTEXT:
{data_context}

USER QUESTION: {question}

Provide a helpful, focused response based on the data above. If the question is outside your domain, politely explain that you can only assist with domain-specific queries."""

        if stream:
            # Return generator for streaming
            response = model.generate_content(full_prompt, stream=True)
            return response
        else:
            # Return complete response
            response = model.generate_content(full_prompt)
            return response.text
            
    except Exception as e:
        error_str = str(e)
        
        # Handle rate limit/quota errors with helpful messages
        if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
            error_msg = """⚠️ **API Quota Exceeded**

**Issue:** The free tier API quota has been reached for this model.

**Solutions:**
1. **Wait a few minutes** - Free tier quotas reset periodically
2. **Try a different model** - Switch to `gemini-1.5-flash` or `gemini-1.5-pro` in the sidebar
3. **Use a different API key** - Get a new key from https://makersuite.google.com/app/apikey
4. **Check usage limits** - Visit https://ai.dev/usage?tab=rate-limit

**Note:** Free tier has daily/minute limits. Consider upgrading for higher quotas."""
        elif "403" in error_str or "API key" in error_str.lower() or "authentication" in error_str.lower():
            error_msg = """🔑 **API Key Error**

**Issue:** Invalid or expired API key.

**Solutions:**
1. Check your API key is correct
2. Verify the key is active at https://makersuite.google.com/app/apikey
3. Try entering a new key in the sidebar
4. Make sure the key hasn't been revoked"""
        else:
            error_msg = f"❌ **Error:** {error_str}\n\nPlease try again or check your connection."
        
        if stream:
            return iter([error_msg])  # Return iterable for consistency
        return error_msg


def query_gemini_streaming(
    question: str,
    system_prompt: str,
    data_context: str,
    api_key: str,
    model_name: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_retries: int = 2
) -> Generator:
    """
    Query Gemini with streaming enabled (word-by-word response).
    Following Week 10 Lab streaming pattern.
    Includes retry logic for rate limits.
    
    Yields:
        Chunks of response text
    """
    error_str = ""
    
    for attempt in range(max_retries + 1):
        try:
            configure_gemini(api_key)
            
            generation_config = get_generation_config(temperature=temperature)
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config
            )
            
            full_prompt = f"""{system_prompt}

CURRENT DATABASE CONTEXT:
{data_context}

USER QUESTION: {question}

Provide a helpful, focused response based on the data above."""

            response = model.generate_content(full_prompt, stream=True)
            
            # Success - yield chunks
            for chunk in response:
                if chunk.text:
                    yield chunk.text
            return  # Success, exit function
                
        except Exception as e:
            error_str = str(e)
            
            # Check if it's a rate limit error
            if "429" in error_str or "quota" in error_str.lower():
                # Extract retry delay if available
                retry_delay = 15  # Default 15 seconds
                if "retry_delay" in error_str.lower():
                    # Try to extract seconds from error message
                    import re
                    match = re.search(r'seconds[:\s]+(\d+)', error_str)
                    if match:
                        retry_delay = int(match.group(1))
                
                if attempt < max_retries:
                    # Wait and retry
                    yield f"⏳ Rate limit reached. Retrying in {retry_delay} seconds...\n\n"
                    time.sleep(retry_delay)
                    continue
                else:
                    # Max retries reached
                    error_msg = f"""⚠️ **API Quota Exceeded**

**Issue:** The free tier quota has been reached for `{model_name}`.

**Solutions:**
1. **Wait {retry_delay} seconds** and try again
2. **Switch to a different model** - Try `gemini-1.5-flash` in the sidebar
3. **Use a different API key** - Get a new key from https://makersuite.google.com/app/apikey
4. **Check your quota** - Visit https://ai.dev/usage?tab=rate-limit

**Note:** Free tier has daily/minute limits. The quota will reset automatically."""
                    yield error_msg
                    return
            else:
                # Other errors - don't retry
                break
    
    # Handle other errors
    if "403" in error_str or "API key" in error_str.lower():
        error_msg = """🔑 **API Key Error**

**Issue:** Invalid or expired API key.

**Solutions:**
1. Check your API key is correct
2. Verify the key at https://makersuite.google.com/app/apikey
3. Enter a new key in the sidebar"""
    else:
        error_msg = f"❌ **Error:** {error_str}\n\nPlease try again or check your connection."
    
    yield error_msg


# ============================================================
# DOMAIN-SPECIFIC ASSISTANT FUNCTIONS
# ============================================================

def query_cybersecurity_assistant(
    question: str, 
    incidents_df: pd.DataFrame, 
    api_key: str,
    model_name: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    stream: bool = False
) -> str | Generator:
    """Query the Cybersecurity AI assistant."""
    data_context = dataframe_to_context(incidents_df)
    return query_gemini(
        question=question,
        system_prompt=SYSTEM_PROMPTS["cybersecurity"],
        data_context=data_context,
        api_key=api_key,
        model_name=model_name,
        temperature=temperature,
        stream=stream
    )


def query_datascience_assistant(
    question: str, 
    datasets_df: pd.DataFrame, 
    api_key: str,
    model_name: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    stream: bool = False
) -> str | Generator:
    """Query the Data Science AI assistant."""
    data_context = dataframe_to_context(datasets_df)
    return query_gemini(
        question=question,
        system_prompt=SYSTEM_PROMPTS["datascience"],
        data_context=data_context,
        api_key=api_key,
        model_name=model_name,
        temperature=temperature,
        stream=stream
    )


def query_itoperations_assistant(
    question: str, 
    tickets_df: pd.DataFrame, 
    api_key: str,
    model_name: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    stream: bool = False
) -> str | Generator:
    """Query the IT Operations AI assistant."""
    data_context = dataframe_to_context(tickets_df)
    return query_gemini(
        question=question,
        system_prompt=SYSTEM_PROMPTS["itoperations"],
        data_context=data_context,
        api_key=api_key,
        model_name=model_name,
        temperature=temperature,
        stream=stream
    )


# Export constants for backward compatibility
API_KEY_CYBERSECURITY = "GEMINI_API_KEY_CYBERSECURITY"
API_KEY_DATASCIENCE = "GEMINI_API_KEY_DATASCIENCE"
API_KEY_ITOPERATIONS = "GEMINI_API_KEY_ITOPERATIONS"

