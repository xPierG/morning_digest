from google.adk.agents import LlmAgent
from client import ReadwiseClient
import json
from utils import fetch_prompt

ENRICHER_PROMPT_URL = "https://gist.githubusercontent.com/xPierG/b7a6f58a369f49120417e3c405973d75/raw/prompt_morning_digest_enricher.txt"

DEFAULT_ENRICHER_PROMPT = """
    You are the "Morning Digest" AI Researcher.
    
    You will receive a JSON object containing a list of selected articles under the key "selection".
    
    YOUR TASK:
    Iterate through the articles and enrich them with "Key Takeaways" ONLY if they belong to specific categories.
    
    RULES:
    1. Identify articles where 'category_label' contains "Non puoi ignorarlo", "must_read", "Lettura Lunga", or "long_read".
    2. For EACH of these target articles:
       - Call the `fetch_full_content` tool with the article's `id`.
       - Analyze the full text.
       - Generate exactly 3 "Key Takeaways" (bullet points) that are valuable for a Chief AI Officer.
       - Add a new field "key_takeaways" (list of strings) to the article object.
    3. For other articles, leave them as is (do NOT add "key_takeaways").
    4. Return the modified JSON object with the "selection" list.
    
    INPUT FORMAT:
    ```json
    {
      "selection": [ ... ]
    }
    ```
    
    OUTPUT FORMAT:
    Return the exact same JSON structure, but with the added "key_takeaways" field for the target articles.
    Output ONLY the JSON.
    """

# Initialize client
client = ReadwiseClient()

# Define tool wrapper
def fetch_full_content(doc_id: str):
    """
    Fetches the full content of a specific document by ID using Readwise API.
    """
    print(f">> TOOL CALL: Fetching full content for {doc_id}...")
    return client.fetch_document_details(doc_id)

# Define Enricher Agent
enricher_agent = LlmAgent(
    name="EnricherAgent",
    model="gemini-2.0-flash-001",
    instruction=fetch_prompt(ENRICHER_PROMPT_URL, DEFAULT_ENRICHER_PROMPT),
    tools=[fetch_full_content],
    output_key="final_digest"
)
