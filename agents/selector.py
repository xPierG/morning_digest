from google.adk.agents import LlmAgent
from google.genai import types
from client import ReadwiseClient
import os
import json

# Initialize client
client = ReadwiseClient()

# Define tool wrapper
def fetch_readwise_data():
    """
    Fetches the latest articles from Readwise Reader (last 24h).
    Returns a simplified list of articles with id, title, summary, source_location, and word_count.
    """
    print(">> TOOL CALL: Fetching data from Readwise...")
    docs = client.fetch_last_24h()
    
    simplified_docs = []
    for doc in docs:
        simplified_docs.append({
            'id': doc.get('id'),
            'title': doc.get('title'),
            'summary': doc.get('summary'),
            'source_location': doc.get('source_location'),
            'word_count': doc.get('word_count', 0),
            'source_url': doc.get('source_url')
        })
    return json.dumps(simplified_docs)

# Define Selector Agent
selector_agent = LlmAgent(
    name="SelectorAgent",
    model="gemini-2.0-flash-001",
    instruction="""
    You are the "Morning Digest" AI Editor for a Chief AI Officer.
    
    Your goal is to select exactly 5 articles from the fetched list to send in a daily email.
    
    STEP 1: Call the `fetch_readwise_data` tool to get the latest articles.
    
    STEP 2: Select exactly 5 articles following this strict priority order:
    1. [1 Article] "🤯 Non puoi ignorarlo" (Category: 'must_read'): 
       - MUST come from "Source Location: feed".
       - The most conceptually novel article. Something not mentioned recently, a new signal.
    2. [1-2 Articles] "📌 Rilevanza CEO / Credem" (Category: 'business'): 
       - Can come from 'feed' OR 'library'.
       - Articles matching keywords like "Modelli Fondazionali", "Banking as a Service", "Fintech", "RegTech", "Algorithmic Risk", "AI Ethics", "Tokenization".
    3. [1 Article] "🧘 Lettura Lunga / Sviluppo Personale" (Category: 'long_read'): 
       - MUST come from "Source Location: library" (or be > 2000 words).
       - A deep dive or personal development piece.
    4. [Remainder] "💡 Altro" (Category: 'other'): 
       - Interesting articles similar to what a CTO/CAIO would like.

    OUTPUT FORMAT:
    Return a JSON object with a key "selection" containing a list of exactly 5 objects.
    Each object must have:
    - "id": The ID of the original document.
    - "title": The title.
    - "category_label": The label for the category.
    - "reasoning": A brief explanation of why this was picked.
    - "source_url": The URL.
    - "summary": The original summary.
    
    Output ONLY the JSON.
    """,
    tools=[fetch_readwise_data],
    output_key="selection_result"
)
