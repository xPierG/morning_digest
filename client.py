import os
import requests
from datetime import datetime, timedelta
import json

class ReadwiseClient:
    def __init__(self, token=None):
        self.token = token or os.getenv("READWISE_TOKEN")
        self.base_url = "https://readwise.io/api/v3"
        
    def fetch_last_24h(self):
        """
        Fetches documents from Readwise Reader updated in the last 24 hours.
        If no token is provided, returns mock data for testing.
        """
        if not self.token:
            print("Warning: No READWISE_TOKEN found. Using mock data.")
            return self._get_mock_data()

        # Calculate timestamp for 24h ago
        after_date = (datetime.now() - timedelta(hours=24)).isoformat()
        
        headers = {"Authorization": f"Token {self.token}"}
        
        all_docs = []
        
        # 1. Fetch from 'new' (Feed/Inbox)
        params_new = {
            "updatedAfter": after_date,
            "location": "new", 
            "page_size": 50
        }
        try:
            response = requests.get(f"{self.base_url}/list/", headers=headers, params=params_new)
            response.raise_for_status()
            new_docs = response.json().get("results", [])
            for d in new_docs: d['source_location'] = 'feed'
            all_docs.extend(new_docs)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching NEW: {e}")

        # 2. Fetch from 'later' (Library)
        params_later = {
            "updatedAfter": after_date,
            "location": "later", 
            "page_size": 50
        }
        try:
            response = requests.get(f"{self.base_url}/list/", headers=headers, params=params_later)
            response.raise_for_status()
            later_docs = response.json().get("results", [])
            for d in later_docs: d['source_location'] = 'library'
            all_docs.extend(later_docs)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching LATER: {e}")
            
        return all_docs

    def fetch_document_details(self, doc_id: str) -> str:
        """
        Fetches the full content of a specific document by ID.
        """
        if not self.token:
            return "Mock full content: This is a placeholder for the full text of the article."

        headers = {"Authorization": f"Token {self.token}"}
        try:
            # Reader API v3 uses /list/ to get document details by ID
            params = {"ids": doc_id}
            response = requests.get(f"{self.base_url}/list/", headers=headers, params=params)
            response.raise_for_status()
            results = response.json().get("results", [])
            if results:
                data = results[0]
                # Return HTML content or plain text if available
                return data.get("html_content") or data.get("summary") or "No content available."
            return "Document not found."
        except requests.exceptions.RequestException as e:
            print(f"Error fetching document details {doc_id}: {e}")
            return ""

    def _get_mock_data(self):
        """Returns a list of mock documents for testing."""
        return [
            {
                "id": "1",
                "title": "The Future of Generative AI in Banking",
                "author": "TechCrunch",
                "source_url": "https://techcrunch.com/ai-banking",
                "published_date": (datetime.now() - timedelta(hours=2)).isoformat(),
                "summary": "An in-depth look at how Modelli Fondazionali are reshaping Fintech.",
                "category": "article",
                "word_count": 1500,
                "tags": {},
                "source_location": "feed"
            },
            {
                "id": "2",
                "title": "Understanding Algorithmic Risk",
                "author": "RiskNet",
                "source_url": "https://risknet.com/algo",
                "published_date": (datetime.now() - timedelta(hours=5)).isoformat(),
                "summary": "Rischio Algoritmico is a growing concern for regulators.",
                "category": "article",
                "word_count": 800,
                "tags": {},
                "source_location": "feed"
            },
            {
                "id": "3",
                "title": "Deep Dive: Tokenization of Assets",
                "author": "CryptoDaily",
                "source_url": "https://crypto.com/token",
                "published_date": (datetime.now() - timedelta(hours=10)).isoformat(),
                "summary": "Tokenizzazione is the next big thing in Banking as a Service.",
                "category": "article",
                "word_count": 3000, # Long read
                "tags": {},
                "source_location": "library"
            },
            {
                "id": "4",
                "title": "10 Tips for Better Sleep",
                "author": "HealthLine",
                "source_url": "https://health.com/sleep",
                "published_date": (datetime.now() - timedelta(hours=12)).isoformat(),
                "summary": "How to sleep better.",
                "category": "article",
                "word_count": 500,
                "tags": {},
                "source_location": "feed"
            },
             {
                "id": "5",
                "title": "New RegTech Solutions for 2025",
                "author": "FinTech World",
                "source_url": "https://fintech.com/regtech",
                "published_date": (datetime.now() - timedelta(hours=1)).isoformat(),
                "summary": "RegTech is evolving rapidly with AI.",
                "category": "article",
                "word_count": 1200,
                "tags": {},
                "source_location": "library"
            },
            {
                "id": "6",
                "title": "A very obscure tech topic",
                "author": "Niche Blog",
                "source_url": "https://niche.com/topic",
                "published_date": (datetime.now() - timedelta(hours=3)).isoformat(),
                "summary": "Something completely new and unheard of.",
                "category": "article",
                "word_count": 600,
                "tags": {},
                "source_location": "feed"
            }
        ]
