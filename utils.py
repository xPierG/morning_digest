import requests
import logging

logger = logging.getLogger(__name__)

def fetch_prompt(url: str, default_prompt: str) -> str:
    """
    Fetches prompt from URL. Returns default_prompt on failure.
    
    Args:
        url (str): The URL to fetch the prompt from (e.g., raw Gist URL).
        default_prompt (str): The fallback prompt to use if fetching fails.
        
    Returns:
        str: The fetched prompt or the default prompt.
    """
    try:
        # Timeout set to 3 seconds to avoid delaying agent startup too much
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        logger.info(f"Successfully fetched prompt from {url}")
        return response.text
    except Exception as e:
        logger.warning(f"Failed to fetch prompt from {url}: {e}. Using default prompt.")
        return default_prompt
