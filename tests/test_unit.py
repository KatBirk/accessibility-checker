# Unit tests - minimal, only test pure functions that exist in main.py
import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock


class TestBasicFunctions:
    """Test the few pure functions that actually exist in main.py"""
    
    def test_testWebsite_returns_violation_count(self, tmp_path, monkeypatch):
        """Test that testWebsite returns integer count of violations"""
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import main
        
        # Run test in isolated temporary directory
        monkeypatch.chdir(tmp_path)
        
        # Mock the entire playwright chain
        with patch('main.sync_playwright') as mock_playwright:
            # Setup mock browser that returns 3 violations
            mock_browser = MagicMock()
            mock_page = MagicMock()
            mock_axe = MagicMock()
            
            mock_playwright.return_value.__enter__.return_value.firefox.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            
            # Setup axe to return sample violations
            main.axe = mock_axe
            mock_axe.run.return_value = {
                "violations": [
                    {"id": "test1", "impact": "serious"},
                    {"id": "test2", "impact": "critical"},
                    {"id": "test3", "impact": "moderate"}
                ]
            }
            
            original_cwd = os.getcwd()
            result = main.testWebsite("https://example.com")
            
            # create count of violations
            assert result == 3
            assert isinstance(result, int)
            
            # should create violations.json
            assert os.path.exists("violations.json")
            
    
    def test_start_server_creates_http_server(self):
        """Test that start_server creates an HTTP server"""
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import main
        
        # Test server creation
        server = main.start_server(port=8001)
        assert server is not None
        assert server.server_address[1] == 8001
        server.shutdown()
