"""Runtime LLM provider resolver — OpenAI / Azure / Groq / Gemini, chosen by env.

Set LLM_PROVIDER (openai|azure|groq|gemini) and the matching key. For OpenAI/Groq/Gemini the
base URL is known; for Azure also set LLM_BASE_URL (your <resource>/openai/v1 endpoint) and
LLM_MODEL (the deployment name). Explicit LLM_BASE_URL / LLM_MODEL / LLM_API_KEY override any
preset, so any OpenAI-compatible endpoint works.
"""
import os
from openai import OpenAI

# provider -> (base_url, default_model, key_env)
_PRESETS = {
    "openai": ("https://api.openai.com/v1", "gpt-4o-mini", "OPENAI_API_KEY"),
    "groq":   ("https://api.groq.com/openai/v1", "llama-3.3-70b-versatile", "GROQ_API_KEY"),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai/", "gemini-1.5-flash", "GEMINI_API_KEY"),
    "azure":  (None, "gpt-4o", "AZURE_GPT4O_KEY"),  # set LLM_BASE_URL to the Azure /openai/v1 endpoint
}


def get_chat_client():
    """Return (OpenAI client, model_name) for the configured provider. If LLM_PROVIDER is unset it is
    auto-detected from the available key, so the app runs with whatever chat key you have — e.g. an
    Azure GPT-4o key alone (AZURE_GPT4O_KEY/_ENDPOINT/_DEPLOYMENT), no OpenAI key needed."""
    provider = os.getenv("LLM_PROVIDER", "").lower()
    if not provider:
        if os.getenv("AZURE_GPT4O_KEY") or "azure" in (os.getenv("LLM_BASE_URL") or "").lower():
            provider = "azure"
        elif os.getenv("GROQ_API_KEY"):
            provider = "groq"
        elif os.getenv("GEMINI_API_KEY"):
            provider = "gemini"
        else:
            provider = "openai"
    base_url, default_model, key_env = _PRESETS.get(provider, _PRESETS["openai"])
    base_url = os.getenv("LLM_BASE_URL") or (os.getenv("AZURE_GPT4O_ENDPOINT") if provider == "azure" else None) or base_url
    model = os.getenv("LLM_MODEL") or (os.getenv("AZURE_GPT4O_DEPLOYMENT") if provider == "azure" else None) or default_model
    api_key = os.getenv("LLM_API_KEY") or os.getenv(key_env) or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            f"No API key for LLM provider '{provider}'. Set LLM_API_KEY or {key_env} in the environment."
        )
    return OpenAI(base_url=base_url or None, api_key=api_key), model
