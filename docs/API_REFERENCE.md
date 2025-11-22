# API Reference

This document provides a high-level reference for the key Python modules in the **Reader Morning Digest** project.

## `main.py`

The entry point for the application.

- **`main()`**: Orchestrates the daily digest generation process. It initializes the `Agent` and `Client`, fetches data, generates the digest, and triggers the notification.

## `agent.py`

Contains the logic for the AI agent.

### `class Agent`

- **`__init__(client: Client)`**: Initializes the agent with a client instance.
- **`generate_digest(context: str) -> str`**: Generates a daily digest based on the provided context string. It constructs the prompt and calls the client to get the response.

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
