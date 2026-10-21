"""
LangChain Model Factory for Groq Cloud and Google DeepMind LLMs.
Uses langchain-groq and langchain-google-genai integrations as demonstrated in notebooks.
"""
from typing import Optional
from langchain_core.language_models import BaseChatModel
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import settings

def get_langchain_model(model_id: str, temperature: float = 0.1) -> Optional[BaseChatModel]:
    """
    Instantiates the appropriate LangChain Chat Model:
    - ChatGroq for Groq-hosted open-weights models
    - ChatGoogleGenerativeAI for Google DeepMind models
    Returns None if the required API key is not configured.
    """
    model_lower = model_id.lower()
    
    # 1. Groq Cloud Models (ChatGroq)
    if "gpt-oss" in model_lower or "groq" in model_lower:
        if not settings.GROQ_API_KEY:
            return None
        
        # Use exact model id (e.g. openai/gpt-oss-120b) or fallback
        groq_model_name = model_id if ("/" in model_id) else ("openai/gpt-oss-120b" if "120b" in model_lower else "openai/gpt-oss-20b")
        return ChatGroq(
            model=groq_model_name,
            groq_api_key=settings.GROQ_API_KEY,
            temperature=temperature,
            max_tokens=1024,
            max_retries=2
        )

    # 2. Google DeepMind Models (ChatGoogleGenerativeAI)
    if "gemini" in model_lower or "gemma" in model_lower:
        if not settings.GEMINI_API_KEY:
            return None
            
        if "3.1-flash-lite" in model_lower or "flash-lite" in model_lower:
            google_model_name = "gemini-3.1-flash-lite"
        elif "gemma" in model_lower:
            google_model_name = "gemma-4-26b-a4b-it"
        elif "pro" in model_lower:
            google_model_name = "gemini-pro-latest"
        else:
            google_model_name = "gemini-flash-latest"

        return ChatGoogleGenerativeAI(
            model=google_model_name,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=temperature,
            max_output_tokens=1024,
            max_retries=2
        )

    # Default fallback to Groq if key exists, else Google
    if settings.GROQ_API_KEY:
        return ChatGroq(
            model=settings.GROQ_MODEL_PRIMARY or "openai/gpt-oss-120b",
            groq_api_key=settings.GROQ_API_KEY,
            temperature=temperature,
            max_tokens=1024,
            max_retries=2
        )
    elif settings.GEMINI_API_KEY:
        return ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=temperature,
            max_output_tokens=1024,
            max_retries=2
        )

    return None
