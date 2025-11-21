import unittest
from unittest.mock import MagicMock, patch
import json
from google.adk.agents import SequentialAgent
from agents.selector import selector_agent
from agents.enricher import enricher_agent

class TestAdkPipeline(unittest.TestCase):

    def test_pipeline_structure(self):
        """Verify the pipeline is constructed correctly with sub-agents."""
        pipeline = SequentialAgent(
            name="TestPipeline",
            sub_agents=[selector_agent, enricher_agent]
        )
        self.assertEqual(pipeline.name, "TestPipeline")
        self.assertEqual(len(pipeline.sub_agents), 2)
        self.assertEqual(pipeline.sub_agents[0].name, "SelectorAgent")
        self.assertEqual(pipeline.sub_agents[1].name, "EnricherAgent")

    @patch('agents.selector.client')
    def test_selector_tool_call(self, mock_client):
        """Verify SelectorAgent uses the fetch tool."""
        # Mock client response
        mock_client.fetch_last_24h.return_value = [
            {'id': '1', 'title': 'Test Doc', 'summary': 'Summary', 'source_location': 'feed'}
        ]
        
        # We can't easily run the full LlmAgent without a real model or complex mocking of the Runner.
        # But we can verify the tool function wrapper in selector.py
        from agents.selector import fetch_readwise_data
        
        result_json = fetch_readwise_data()
        result = json.loads(result_json)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], '1')
        mock_client.fetch_last_24h.assert_called_once()

    @patch('agents.enricher.client')
    def test_enricher_tool_call(self, mock_client):
        """Verify EnricherAgent uses the fetch details tool."""
        mock_client.fetch_document_details.return_value = "Full content"
        
        from agents.enricher import fetch_full_content
        
        content = fetch_full_content("123")
        self.assertEqual(content, "Full content")
        mock_client.fetch_document_details.assert_called_with("123")

if __name__ == '__main__':
    unittest.main()
