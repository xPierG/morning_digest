# 🌅 Morning Digest AI Agent

An intelligent agent that curates a daily "Top 5" reading list from your **Readwise Reader** account, powered by **Google Gemini 2.0 Flash** and built with the **Google Agent Development Kit (ADK)**.

## Features

- **🧠 Modular ADK Architecture**: Built with Google ADK using specialized `LlmAgent` components orchestrated by a `SequentialAgent`.
- **🤖 Two-Stage Pipeline**:
  - **SelectorAgent**: Autonomously fetches and selects exactly 5 articles based on predefined criteria.
  - **EnricherAgent**: Enriches selected articles with full content and generates 3 key takeaways for high-priority items.
- **📂 Dual Source**: Fetches content from both your **Feed** (RSS/Newsletters) and **Library** (Saved/Inbox).
- **🎯 Smart Categorization**:
  - **🤯 Must Read**: Novel concepts and new signals (from Feed).
  - **📌 Business**: Relevant to your specific domain (e.g., AI, Fintech).
  - **🧘 Long Read**: Deep dives for personal development (from Library).
  - **💡 Other**: Interesting articles for CTO/CAIO.
- **🔧 Robust Error Handling**: Automatic JSON repair and async/await support for reliable execution.

## Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/xPierG/morning_digest.git
   cd morning_digest
   ```

2. **Configure Environment**:
   Copy the example file and add your API keys:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and fill in:
   - `READWISE_TOKEN`: Get it from [Readwise Access Token](https://readwise.io/access_token).
   - `GOOGLE_API_KEY`: Get it from [Google AI Studio](https://aistudio.google.com/app/apikey).

3. **Install Dependencies**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

## Usage

### Run Locally
```bash
source .venv/bin/activate
python main.py
```
The agent will fetch the latest articles, select the top 5, enrich them with key takeaways, and generate a `daily_digest.md` file.

### Run with Docker
```bash
docker build -t morning-digest .
docker run --env-file .env morning-digest
```

## Architecture

The project uses **Google Agent Development Kit (ADK)** with a modular, sequential pipeline:

- **`agents/selector.py`**: `SelectorAgent` - Fetches articles from Readwise and selects exactly 5 based on category criteria.
- **`agents/enricher.py`**: `EnricherAgent` - Enriches "Must Read" and "Long Read" articles with full content and generates 3 key takeaways.
- **`agent.py`**: `MorningDigestPipeline` - A `SequentialAgent` that orchestrates the two specialized agents.
- **`client.py`**: Handles interactions with the Readwise API (fetching articles and full content).
- **`main.py`**: Entry point using `InMemoryRunner` to execute the ADK pipeline asynchronously.

## License
MIT
