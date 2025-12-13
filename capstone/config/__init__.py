"""Configuration module for the Smart Grading Assistant."""

from .settings import (
    APP_NAME,
    USER_ID,
    BASE_DIR,
    LOG_PATH,
    DATA_DIR,
    MODEL_LITE,
    MODEL,
    LLM_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_MODEL,
    DEFAULT_MODEL,
    FAILING_THRESHOLD,
    EXCEPTIONAL_THRESHOLD,
    retry_config,
)

__all__ = [
    "APP_NAME",
    "USER_ID",
    "BASE_DIR",
    "LOG_PATH",
    "DATA_DIR",
    "MODEL_LITE",
    "MODEL",
    "LLM_PROVIDER",
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "OPENAI_MODEL",
    "DEFAULT_MODEL",
    "FAILING_THRESHOLD",
    "EXCEPTIONAL_THRESHOLD",
    "retry_config",
]
