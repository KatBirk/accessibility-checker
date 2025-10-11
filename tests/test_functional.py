# Functional tests - test real main.py functions with controlled inputs
import pytest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock


class TestMainFunctions:
    """Test actual main.py functions with mocked dependencies"""
    
    def test_testWebsite_full_workflow(self):
        """Test the complete testWebsite function workflow"""
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import main
        
        # Use current directory, clean up test files manually
        # Mock playwright but use real function logic
        with patch('main.sync_playwright') as mock_playwright:
            # Setup realistic mock browser
            mock_context = MagicMock()
            mock_browser = MagicMock()
            mock_page = MagicMock()
            
            mock_playwright.return_value.__enter__.return_value = mock_context
            mock_context.firefox.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            
            # Mock axe with realistic violation data
            main.axe = MagicMock()
            realistic_violations = [
                {
                    "id": "color-contrast",
                    "impact": "serious",
                    "description": "Color contrast issue",
                    "nodes": [{"html": "<div>Low contrast</div>"}]
                },
                {
                    "id": "missing-alt",
                    "impact": "critical", 
                    "description": "Missing alt text",
                    "nodes": [{"html": "<img src='test.jpg'>"}]
                }
            ]
            main.axe.run.return_value = {"violations": realistic_violations}
            
            # Call the real function
            result = main.testWebsite("https://test-site.com")
            
            # Verify function behavior
            assert result == 2
            mock_page.goto.assert_called_once_with("https://test-site.com")
            main.axe.run.assert_called_once_with(mock_page)
            mock_browser.close.assert_called_once()
            
            # Verify JSON output
            assert os.path.exists("violations.json")
            with open("violations.json", "r") as f:
                data = json.load(f)
            
            assert len(data) == 2
            assert data[0]["id"] == "color-contrast"
            assert data[1]["id"] == "missing-alt"
            
            if os.path.exists("violations.json"):
                os.remove("violations.json")

    # Probably not needed, but just in case
    def test_start_progress_workflow_integration(self):
        """Test that start_progress integrates its components correctly"""
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import main
        
        # Mock all the external dependencies
        with patch('main.sitemap.sitemapsFromUrl') as mock_sitemap, \
             patch('main.testWebsite') as mock_testWebsite:
            
            # Setup controlled test data
            mock_sitemap.return_value = [
                "https://example.com/page1",
                "https://example.com/page2"
            ]
            mock_testWebsite.side_effect = [3, 5]  # Return 3 violations, then 5
            
            # Mock GUI components that start_progress expects
            class MockProgress:
                def __init__(self):
                    self.value = 0
                def start(self): pass
                def stop(self): pass
                def __setitem__(self, key, value): 
                    self.value = value
            
            class MockLabel:
                def __init__(self):
                    self.text = ""
                def config(self, text=""): 
                    self.text = text
            
            class MockRoot:
                def update_idletasks(self): pass
            
            # Setup global state like main.py does
            main.websiteToBESCANNED = "https://example.com"
            main.vioCount = 0
            main.progress = MockProgress()
            main.laban = MockLabel()
            main.root = MockRoot()
            main.stopwatch = main.Stopwatch()
            
            # Call the real function
            main.start_progress()
            
            # Verify the workflow worked correctly
            mock_sitemap.assert_called_once_with("https://example.com")
            assert mock_testWebsite.call_count == 2  # Should scan 2 URLs
            mock_testWebsite.assert_any_call("https://example.com/page1")
            mock_testWebsite.assert_any_call("https://example.com/page2")
            
            # Verify violation count aggregation
            assert main.vioCount == 8  # 3 + 5 violations
            
            # Verify final message shows total violations
            assert "8 violations found" in main.laban.text
            
            # Verify progress reached 100%
            assert main.progress.value == 100.0
    

