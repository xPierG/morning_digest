import os
import json
import google.generativeai as genai
from typing import List, Dict
from client import ReadwiseClient

class MorningDigestAgent:
    def __init__(self):
        # Configure Gemini
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("Warning: GOOGLE_API_KEY not found. Agent will fail if called.")
        else:
            genai.configure(api_key=api_key)
            
        self.client = ReadwiseClient()
        
        # Define the tool
        # We wrap the client method to be a standalone function or bound method we can pass
        self.tools = [self._fetch_readwise, self._fetch_full_content]
        
        self.model = genai.GenerativeModel(
            'gemini-flash-latest',
            tools=self.tools
        )

    def _fetch_readwise(self):
        """
        Fetches the list of articles and documents from Readwise Reader (last 24 hours).
        Returns a JSON string containing the documents from both Feed and Library.
        """
        print(">> TOOL CALL: Fetching data from Readwise...")
        docs = self.client.fetch_last_24h()
        # Optimize context: Select only relevant fields to save tokens if needed, 
        # but Flash has 1M context so we are good.
        simplified_docs = []
        for doc in docs:
            simplified_docs.append({
                "id": doc.get("id"),
                "title": doc.get("title"),
                "summary": doc.get("summary"),
                "source_url": doc.get("source_url"),
                "word_count": doc.get("word_count"),
                "source_location": doc.get("source_location")
            })
        return json.dumps(simplified_docs)

    def _fetch_full_content(self, doc_id: str):
        """
        Fetches the full content of a specific document by ID using Readwise API.
        """
        print(f">> TOOL CALL: Fetching full content for {doc_id}...")
        return self.client.fetch_document_details(doc_id)

    def run(self) -> List[Dict]:
        """
        Executes the agent loop:
        1. Asks LLM to fetch data and select Top 5.
        2. For specific categories, fetches full content and enriches with Key Takeaways.
        """
        # Enable automatic function calling for the first step
        chat = self.model.start_chat(enable_automatic_function_calling=True)

        prompt = """
        You are the "Morning Digest" AI Editor for a Chief AI Officer.
        
        STEP 1: Fetch the latest articles using the `_fetch_readwise` tool.
        
        STEP 2: Select exactly 5 articles from the fetched list to send in a daily email.
        
        The selection MUST follow this strict priority order:
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
        
        Do not include markdown formatting (like ```json) in the response, just the raw JSON string.
        """

        try:
            # Step 1: Selection
            response = chat.send_message(prompt)
            response_text = response.text.strip()
            
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
                
            data = json.loads(response_text)
            selection = data.get("selection", [])
            
            # Step 2: Targeted Enrichment
            print(">> ENRICHMENT: Analyzing 'Must Read' and 'Long Read' articles...")
            for doc in selection:
                category = doc.get('category_label', '')
                # Check if category matches our target for enrichment
                if 'Non puoi ignorarlo' in category or 'Lettura Lunga' in category or 'must_read' in category or 'long_read' in category:
                    doc_id = doc.get('id')
                    full_content = self._fetch_full_content(doc_id)
                    
                    # Ask LLM to generate Key Takeaways based on full content
                    enrich_prompt = f"""
                    Analyze the following full text of an article.
                    Generate exactly 3 "Key Takeaways" (bullet points) that are valuable for a Chief AI Officer.
                    Be concise, actionable, and insightful.
                    
                    FULL TEXT:
                    {full_content[:50000]} # Limit context just in case
                    
                    OUTPUT FORMAT:
                    Return a JSON object with a key "key_takeaways" containing a list of 3 strings.
                    """
                    
                    try:
                        enrich_response = self.model.generate_content(enrich_prompt)
                        enrich_text = enrich_response.text.strip()
                        if enrich_text.startswith("```json"):
                            enrich_text = enrich_text[7:]
                        if enrich_text.endswith("```"):
                            enrich_text = enrich_text[:-3]
                        
                        enrich_data = json.loads(enrich_text)
                        doc['key_takeaways'] = enrich_data.get('key_takeaways', [])
                        print(f"   -> Enriched: {doc.get('title')}")
                        
                    except Exception as e:
                        print(f"   -> Failed to enrich {doc.get('title')}: {e}")

            return selection

        except Exception as e:
            print(f"Error calling Gemini Agent: {e}")
            return []
