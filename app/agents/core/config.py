"""
app/agents/core/config.py
===========================

Central settings for all agents using Pydantic BaseSettings.
Values are auto-loaded from the .env file.

Usage:
    from app.agents.core.config import settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Tier 1: Qwen (Primary) ---
    qwen_api_key: str    = ""
    qwen_base_url: str   = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    qwen_model: str      = "qwen-plus"

    # --- Tier 2: Groq (1st Fallback) ---
    groq_api_key: str    = ""
    groq_base_url: str   = "https://api.groq.com/openai/v1"
    groq_model: str      = "llama-3.3-70b-versatile"

    # --- Tier 3: OpenRouter (2nd Fallback) ---
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://api.openrouter.ai/v1"
    openrouter_model: str     = "google/gemini-2.0-flash:free"

    # --- Tier 4: Cerebras (3rd Fallback) ---
    cerebras_api_key: str  = ""
    cerebras_base_url: str = "https://api.cerebras.ai/v1"
    cerebras_model: str     = "llama3.1-70b"

    # --- LLM Shared Settings ---
    summarizer_llm_model: str = "qwen-plus"
    llm_temperature: float = 0.7
    llm_max_tokens: int    = 1024
    llm_timeout: int       = 60
    llm_max_retries: int   = 3

    # --- PIA Workflow ---
    summarize_every_n: int = 8
    initial_module: str    = "SCID_SC"


settings = Settings()
