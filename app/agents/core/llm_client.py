"""
app/agents/core/llm_client.py
================================

Simple async LLM client wrapper.
Config comes from core/config.py (which reads .env).

Usage:
    from app.agents.core.llm_client import get_llm, get_fallback_llm

    llm = get_llm()
    response = await llm.ainvoke(messages)
"""

from langchain_openai import ChatOpenAI
from app.agents.core.config import settings


def get_llm(**kwargs):
    """
    Return the primary LLM (Qwen) with multiple fallbacks:
    1. Groq
    2. OpenRouter
    3. Cerebras
    """
    # Pop model if provided explicitly, otherwise default to qwen
    primary_model = kwargs.pop("model", settings.qwen_model)
    
    # Initialize basic kwargs with defaults
    base_kwargs = kwargs.copy()
    base_kwargs.setdefault("temperature", settings.llm_temperature)
    base_kwargs.setdefault("max_tokens", settings.llm_max_tokens)
    
    # Tier 1: Qwen (Primary)
    primary_kwargs = base_kwargs.copy()
    primary_kwargs.setdefault("timeout", settings.llm_timeout)
    primary_kwargs.setdefault("max_retries", settings.llm_max_retries)
    
    primary = ChatOpenAI(
        model=primary_model,
        api_key=settings.qwen_api_key,
        base_url=settings.qwen_base_url,
        **primary_kwargs
    )

    # Tier 2: Groq (1st Fallback)
    groq_kwargs = base_kwargs.copy()
    groq_kwargs.setdefault("timeout", 30)
    groq_kwargs.setdefault("max_retries", 1)

    fallback_1 = ChatOpenAI(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
        base_url=settings.groq_base_url,
        **groq_kwargs
    )

    # Tier 3: OpenRouter (2nd Fallback)
    openrouter_kwargs = base_kwargs.copy()
    openrouter_kwargs.setdefault("timeout", 30)
    openrouter_kwargs.setdefault("max_retries", 0)

    fallback_2 = ChatOpenAI(
        model=settings.openrouter_model,
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        **openrouter_kwargs
    )

    # Tier 4: Cerebras (3rd Fallback)
    cerebras_kwargs = base_kwargs.copy()
    cerebras_kwargs.setdefault("timeout", 30)
    cerebras_kwargs.setdefault("max_retries", 0)

    fallback_3 = ChatOpenAI(
        model=settings.cerebras_model,
        api_key=settings.cerebras_api_key,
        base_url=settings.cerebras_base_url,
        **cerebras_kwargs
    )

    # Chain them together
    return primary.with_fallbacks([fallback_1, fallback_2, fallback_3])


def get_fallback_llm():
    """Legacy wrapper for compatibility, now just returns the fallback chain."""
    return get_llm()
