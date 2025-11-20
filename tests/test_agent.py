import unittest
from unittest.mock import MagicMock, patch
import json
from agent import MorningDigestAgent

class TestAgent(unittest.TestCase):
    @patch('agent.genai')
    def test_select_top_5_success(self, mock_genai):
        # Mock the model and response
        mock_model = MagicMock()
        mock_response = MagicMock()
        
        # Mock JSON response from LLM
        mock_json = {
            "selection": [
                {"id": "1", "category_label": "Cat1", "reasoning": "Reason 1"},
                {"id": "2", "category_label": "Cat2", "reasoning": "Reason 2"},
                {"id": "3", "category_label": "Cat3", "reasoning": "Reason 3"},
                {"id": "4", "category_label": "Cat4", "reasoning": "Reason 4"},
                {"id": "5", "category_label": "Cat5", "reasoning": "Reason 5"}
            ]
        }
        mock_response.text = json.dumps(mock_json)
        mock_model.generate_content.return_value = mock_response
        
        # Setup agent with mocked model
        agent = MorningDigestAgent()
        agent.model = mock_model
        
        # Input docs
        docs = [{"id": str(i), "title": f"Doc {i}", "summary": "Sum", "source_url": "url"} for i in range(1, 10)]
        
        # Run selection
        selection = agent.select_top_5(docs)
        
        # Verify
        self.assertEqual(len(selection), 5)
        self.assertEqual(selection[0]['id'], "1")
        self.assertEqual(selection[0]['category_label'], "Cat1")
        self.assertEqual(selection[0]['ai_reasoning'], "Reason 1")

    @patch('agent.genai')
    def test_select_top_5_failure_fallback(self, mock_genai):
        # Mock exception
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Error")
        
        agent = MorningDigestAgent()
        agent.model = mock_model
        
        docs = [{"id": str(i), "title": f"Doc {i}", "summary": "Sum", "source_url": "url"} for i in range(1, 10)]
        
        # Run selection (should fallback)
        selection = agent.select_top_5(docs)
        
        self.assertEqual(len(selection), 5)
        self.assertEqual(selection[0]['id'], "1")
        # Should NOT have ai fields
        self.assertNotIn('category_label', selection[0])

if __name__ == '__main__':
    unittest.main()
