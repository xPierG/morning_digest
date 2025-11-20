# 🌅 Morning Digest AI Agent

An intelligent agent that curates a daily "Top 5" reading list from your **Readwise Reader** account, powered by **Google Gemini 1.5 Flash**.

## Features

- **🧠 AI-Powered Selection**: Uses Gemini 1.5 Flash to semantically analyze and select the most relevant articles.
- **🛠️ Agentic Tool Use**: The agent autonomously calls the Readwise API to fetch data when needed.
- **📂 Dual Source**: Fetches content from both your **Feed** (RSS/Newsletters) and **Library** (Saved/Inbox).
- **🎯 Smart Categorization**:
  - **🤯 Must Read**: Novel concepts and new signals (from Feed).
  - **📌 Business**: Relevant to your specific domain (e.g., AI, Fintech).
  - **🧘 Long Read**: Deep dives for personal development (from Library).
- **🐳 Cloud Ready**: Fully containerized with Docker, ready for Google Cloud Run.

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
python main.py
```
The agent will fetch the latest articles, select the top 5, and generate a `daily_digest.md` file.

### Run with Docker
```bash
docker build -t morning-digest .
docker run --env-file .env morning-digest
```

## Architecture

- **`agent.py`**: Contains the `MorningDigestAgent` class which uses Gemini with Tool Use capabilities.
- **`client.py`**: Handles interactions with the Readwise API.
- **`main.py`**: Entry point that initializes the agent and runs the workflow.

## License
MIT
