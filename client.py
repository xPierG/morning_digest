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
        Fetches from both 'feed' (RSS/Newsletters) and 'new' (Library Inbox).
        """
        if not self.token:
            print("Warning: No READWISE_TOKEN found. Using mock data.")
            return self._get_mock_data()

        # Calculate timestamp for 24h ago
        after_date = (datetime.now() - timedelta(hours=24)).isoformat()
        headers = {"Authorization": f"Token {self.token}"}
        
        all_docs = []
        
        # 1. Fetch from Feed
        params_feed = {
            "updatedAfter": after_date,
            "location": "feed", 
            "page_size": 50
        }
        try:
            response = requests.get(f"{self.base_url}/list/", headers=headers, params=params_feed)
            response.raise_for_status()
            feed_docs = response.json().get("results", [])
            for d in feed_docs: d['source_location'] = 'feed'
            all_docs.extend(feed_docs)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching FEED: {e}")

        # 2. Fetch from Library (Inbox/New)
        params_lib = {
            "updatedAfter": after_date,
            "location": "new", 
            "page_size": 50
        }
        try:
            response = requests.get(f"{self.base_url}/list/", headers=headers, params=params_lib)
            response.raise_for_status()
            lib_docs = response.json().get("results", [])
            for d in lib_docs: d['source_location'] = 'library'
            all_docs.extend(lib_docs)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching LIBRARY: {e}")

        return all_docs

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
