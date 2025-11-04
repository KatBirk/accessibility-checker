# Functional tests - test real main.py functions with controlled inputs
import pytest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock


class TestMainFunctions:
    """Test actual main.py functions with mocked dependencies"""
    
    def test_testWebsite_full_workflow(self, tmp_path, monkeypatch):
        """Test the complete testWebsite function workflow"""
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import main
        
        # Run test in isolated temporary directory - won't affect user files
        monkeypatch.chdir(tmp_path)
        
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
            
            # Simulate page with sensitive content that should NOT be stored
            mock_page.content.return_value = """
            <html>
                <head><title>Secret Company Internal Portal</title></head>
                <body>
                    <h1>Confidential User Data: John Doe SSN: 123-45-6789</h1>
                    <div class="sensitive">Private customer information here</div>
                    <img src="logo.jpg"><!-- Missing alt - accessibility violation -->
                    <div style="color: #ccc; background: white;">Low contrast text</div>
                </body>
            </html>
            """
            
            # Mock axe with realistic violation data
            main.axe = MagicMock()
            realistic_violations = [
                {
                    "id": "color-contrast",
                    "impact": "serious",
                    "description": "Color contrast issue",
                    "helpUrl": "https://dequeuniversity.com/rules/axe/4.8/color-contrast",
                    "nodes": [{"html": "<div>Low contrast</div>"}]
                },
                {
                    "id": "missing-alt",
                    "impact": "critical", 
                    "description": "Missing alt text",
                    "helpUrl": "https://dequeuniversity.com/rules/axe/4.8/image-alt",
                    "nodes": [{"html": "<img src='test.jpg'>"}]
                }
            ]
            main.axe.run.return_value = {"violations": realistic_violations}
            
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
            
            # PRIVACY VALIDATION
            json_str = json.dumps(data)
            
            # Verify NO sensitive page content is stored
            assert "Secret Company Internal Portal" not in json_str, "MUST NOT store page titles"
            assert "John Doe SSN: 123-45-6789" not in json_str, "MUST NOT store sensitive data"
            assert "Private customer information" not in json_str, "MUST NOT store private content"
            assert "Confidential User Data" not in json_str, "MUST NOT store confidential data"
            
            # Verify NO HTML structure is stored (only violation nodes should be present)
            assert "<html>" not in json_str, "MUST NOT store full HTML structure"
            assert "<head>" not in json_str, "MUST NOT store head content"
            assert "<body>" not in json_str, "MUST NOT store body content"
            assert "<title>" not in json_str, "MUST NOT store title tags"
            
            # Verify WCAG guidance links are present
            assert "helpUrl" in json_str, "Should provide WCAG guidance links"
            assert "dequeuniversity.com" in json_str, "Should link to authoritative WCAG guidance"
            
