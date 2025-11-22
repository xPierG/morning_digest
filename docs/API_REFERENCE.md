# API Reference

This document provides a high-level reference for the key Python modules in the **Reader Morning Digest** project.

## `main.py`

The entry point for the application.

- **`main()`**: Orchestrates the daily digest generation process. It initializes the `Agent` and `Client`, fetches data, generates the digest, and triggers the notification.

## `agents` Package

Contains the specialized AI agents.

### `agents.selector`

- **`selector_agent`**: An `LlmAgent` configured to select the top 5 articles from the fetched data based on priority categories.
- **`fetch_readwise_data()`**: Tool function to fetch the latest articles from Readwise (last 24h).

### `agents.enricher`

- **`enricher_agent`**: An `LlmAgent` configured to process selected articles and add "Key Takeaways" and reasoning.

## `agent.py` (Legacy/Wrapper)

Contains the pipeline definition.

### `morning_digest_pipeline`
- Defines the flow between `SelectorAgent` and `EnricherAgent`.

## `client.py`

Handles interactions with the LLM API.

### `class Client`

- **`__init__(api_key: str, model: str)`**: Initializes the client with the API key and model name.
- **`generate_content(prompt: str) -> str`**: Sends a prompt to the configured LLM and returns the generated text.

## `notification.py`

Manages email notifications.

### `class NotificationManager`

- **`__init__()`**: Initializes the notification manager, loading SMTP settings from environment variables.
- **`send_digest(content: str)`**: Sends the provided content (Markdown) as an HTML email to the configured recipient.
- **`_convert_to_html(markdown_content: str) -> str`**: Helper method to convert Markdown to HTML with inline styling.
