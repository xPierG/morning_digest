import os
import json
import google.generativeai as genai
from typing import List, Dict

class MorningDigestAgent:
    def __init__(self):
        # Configure Gemini
        # Note: In a real scenario, we might use Vertex AI (google-cloud-aiplatform) 
        # if running on GCP for better integration, but google-generativeai is simpler for the prototype.
        # We'll assume GOOGLE_API_KEY is set.
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("Warning: GOOGLE_API_KEY not found. Agent will fail if called.")
        else:
            genai.configure(api_key=api_key)
            
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def select_top_5(self, documents: List[Dict]) -> List[Dict]:
        """
        Uses Gemini Flash to select the top 5 articles based on the user's criteria.
        """
        if not documents:
            return []

        # Prepare the context for the LLM
        docs_context = ""
        for doc in documents:
            docs_context += f"ID: {doc.get('id')}\n"
            docs_context += f"Title: {doc.get('title')}\n"
            docs_context += f"Summary: {doc.get('summary')}\n"
            docs_context += f"Source URL: {doc.get('source_url')}\n"
            docs_context += f"Word Count: {doc.get('word_count')}\n"
            docs_context += f"Source Location: {doc.get('source_location', 'unknown')}\n" # Feed or Library
            docs_context += "---\n"

        prompt = f"""
        You are the "Morning Digest" AI Editor for a Chief AI Officer.
        Your goal is to select exactly 5 articles from the provided list to send in a daily email.
        
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
        4. [Remainder] "📈 Basato sul Feedback" (Category: 'feedback'): 
           - Interesting articles similar to what a CTO/CAIO would like.

        INPUT DOCUMENTS:
        {docs_context}

        OUTPUT FORMAT:
        Return a JSON object with a key "selection" containing a list of exactly 5 objects.
        Each object must have:
        - "id": The ID of the original document.
        - "category_label": The label for the category (e.g., "🤯 Non puoi ignorarlo").
        - "reasoning": A brief explanation of why this was picked.
        
        Do not include markdown formatting (like ```json) in the response, just the raw JSON string.
        """

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            # Clean up markdown if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
                
            data = json.loads(response_text)
            selected_items = data.get("selection", [])
            
            # Merge back with original doc data
            final_selection = []
            doc_map = {d['id']: d for d in documents}
            
            for item in selected_items:
                original = doc_map.get(item['id'])
                if original:
                    # Enrich original with AI selection metadata
                    original['category_label'] = item['category_label']
                    original['ai_reasoning'] = item['reasoning']
                    final_selection.append(original)
            
            return final_selection

        except Exception as e:
            print(f"Error calling Gemini Agent: {e}")
            # Fallback: return first 5
            return documents[:5]
