"""
LLM configuration for Input Parser Agent
"""

from langchain_groq import ChatGroq
from .config import config

llm = ChatGroq(
    groq_api_key=config.groq.api_key,
    model_name=config.groq.model,
    temperature=config.groq.temperature,
    max_tokens=config.groq.max_tokens,
    timeout=config.groq.timeout
)
