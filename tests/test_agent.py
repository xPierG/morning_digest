import unittest
from unittest.mock import MagicMock, patch
import json
from agent import MorningDigestAgent

class TestAgent(unittest.TestCase):
    @patch('agent.genai')
    def test_run_success(self, mock_genai):
        # Mock the model and chat
        mock_model = MagicMock()
        mock_chat = MagicMock()
        mock_model.start_chat.return_value = mock_chat
        
        # Mock the response from send_message
        mock_response = MagicMock()
        mock_json = {
            "selection": [
                {"id": "1", "title": "T1", "category_label": "Cat1", "reasoning": "Reason 1", "source_url": "u1", "summary": "s1"},
                {"id": "2", "title": "T2", "category_label": "Cat2", "reasoning": "Reason 2", "source_url": "u2", "summary": "s2"},
                {"id": "3", "title": "T3", "category_label": "Cat3", "reasoning": "Reason 3", "source_url": "u3", "summary": "s3"},
                {"id": "4", "title": "T4", "category_label": "Cat4", "reasoning": "Reason 4", "source_url": "u4", "summary": "s4"},
                {"id": "5", "title": "T5", "category_label": "Cat5", "reasoning": "Reason 5", "source_url": "u5", "summary": "s5"}
            ]
        }
        mock_response.text = json.dumps(mock_json)
        mock_chat.send_message.return_value = mock_response
        
        # Setup agent
        agent = MorningDigestAgent()
        agent.model = mock_model
        
        # Run
        selection = agent.run()
        
        # Verify
        self.assertEqual(len(selection), 5)
        self.assertEqual(selection[0]['id'], "1")
        # Verify start_chat was called with auto function calling
        mock_model.start_chat.assert_called_with(enable_automatic_function_calling=True)
        # Verify send_message was called
        mock_chat.send_message.assert_called()

    def test_fetch_readwise_tool(self):
        # Test the tool wrapper
        with patch('agent.ReadwiseClient') as MockClient:
            mock_client_instance = MockClient.return_value
            mock_client_instance.fetch_last_24h.return_value = [{"id": "1", "title": "Test"}]
            
            agent = MorningDigestAgent()
            result_json = agent._fetch_readwise()
            
            result = json.loads(result_json)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['title'], "Test")

if __name__ == '__main__':
    unittest.main()
