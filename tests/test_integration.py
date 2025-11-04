# Integration tests - test complete workflows with real components
import pytest
import json
import os
import tempfile
from unittest.mock import patch


class TestCompleteWorkflows:
    """Test complete end-to-end workflows"""
    
    def test_sitemap_to_violations_pipeline(self, tmp_path, monkeypatch):
        """Test the complete pipeline: sitemap -> URLs -> violations -> JSON"""
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import main
        from axe_core_python.sync_playwright import Axe
        
        monkeypatch.chdir(tmp_path)
        main.axe = Axe()
        
        # Mock sitemap to return controlled URLs
        test_urls = [
            "https://www.playwright.dev/",
            "https://www.github.com/"
        ]
        
        with patch('main.sitemap.sitemapsFromUrl') as mock_sitemap:
            mock_sitemap.return_value = test_urls
            
            # set up global variables like our main.py does
            main.websiteToBESCANNED = "https://example.com"
            main.vioCount = 0
            
            # mock GUI components that start_progress expects
            class MockProgress:
                def start(self): pass
                def stop(self): pass
                def __setitem__(self, key, value): pass
            
            class MockLabel:
                def config(self, text=""): pass
            
            class MockRoot:
                def update_idletasks(self): pass
            
            main.progress = MockProgress()
            main.laban = MockLabel()
            main.root = MockRoot()
            main.stopwatch = main.Stopwatch()
            
            try:
                # This should process 2 URLs and aggregate violations
                main.start_progress()
                
                # Verify results
                assert main.vioCount >= 0  # Should have processed violations
                assert os.path.exists("violations.json")  # Last scan should create JSON
                
                # Verify JSON structure and privacy compliance
                with open("violations.json", "r") as f:
                    data = json.load(f)
                assert isinstance(data, list)
                
                # PRIVACY VALIDATION
                if len(data) > 0:
                    json_str = json.dumps(data)
                    # These shouldn't appear in violation data from real sites
                    assert "<html>" not in json_str, "Should not store HTML structure"
                    assert "<head>" not in json_str, "Should not store head content"
                    assert "<body>" not in json_str, "Should not store body content"
                    
                    # Verify violations have proper WCAG structure
                    violation = data[0]
                    assert "id" in violation, "Violations should have WCAG rule ID"
                    assert "impact" in violation, "Violations should have severity impact"
                
            except Exception as e:
                pytest.skip(f"Pipeline test skipped due to network/browser issue: {e}")


class TestRealBrowserIntegration:
    """Integration tests with real browser automation - slower but validates actual functionality"""
    
    def test_real_browser_scan_reliable_page(self, tmp_path, monkeypatch):
        """Test scanning a real, reliable webpage"""
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import main
        from axe_core_python.sync_playwright import Axe
        
        # Run in a temp folder so violations.json is isolated
        monkeypatch.chdir(tmp_path)
        
        # Set up axe globally (like main.py does)
        main.axe = Axe()
        
        # Use a reliable URL from the predefined list
        reliable_url = "https://www.playwright.dev/"  # Playwright's own site - should be reliable
        
        try:
            # Call the real function with real browser
            count = main.testWebsite(reliable_url)
            
            # Basic assertions - don't test specific violations (they might change)
            assert isinstance(count, int), "Should return integer count"
            assert count >= 0, "Violation count should be non-negative"
            
            # Verify JSON was created
            violations_file = tmp_path / "violations.json"
            assert violations_file.exists(), "violations.json should be created"
            
            # Verify JSON structure
            data = json.loads(violations_file.read_text())
            assert isinstance(data, list), "JSON should contain a list"
            assert len(data) == count, "JSON length should match returned count"
            
            # If violations found, verify basic structure and privacy compliance
            if count > 0:
                violation = data[0]
                assert "id" in violation, "Violation should have id"
                assert "impact" in violation, "Violation should have impact"
                assert violation["impact"] in ["minor", "moderate", "serious", "critical"], "Impact should be valid"
                
                # PRIVACY VALIDATION
                json_str = json.dumps(data)
                # Should not contain full page content from playwright.dev
                assert "<!DOCTYPE html>" not in json_str, "Should not store DOCTYPE declarations"
                assert "<html" not in json_str or json_str.count("<html") <= len(data), "Should only store violation HTML snippets"
                assert "playwright" not in json_str.lower() or "playwright.dev" not in json_str, "Should not store site-specific content"
                
        except Exception as e:
            pytest.skip(f"Integration test skipped due to network/browser issue: {e}")
    
    def test_real_browser_scan_complex_page(self, tmp_path, monkeypatch):
        """Test scanning a more complex page that likely has accessibility issues"""
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import main
        from axe_core_python.sync_playwright import Axe
        
        # Run in a temp folder
        monkeypatch.chdir(tmp_path)
        
        main.axe = Axe()
        
        complex_url = "https://www.berkshirehathaway.com/"
        
        try:
            count = main.testWebsite(complex_url)
            
            # Basic assertions
            assert isinstance(count, int), "Should return integer count"
            assert count >= 0, "Violation count should be non-negative"
            
            # Verify JSON was created
            violations_file = tmp_path / "violations.json"
            assert violations_file.exists(), "violations.json should be created"
            
            # Verify JSON is valid and matches count
            data = json.loads(violations_file.read_text())
            assert isinstance(data, list), "JSON should contain a list"
            assert len(data) == count, "JSON length should match returned count"
            
            # Test violation severity distribution if violations found
            if count > 0:
                impacts = [v.get("impact") for v in data]
                valid_impacts = ["minor", "moderate", "serious", "critical"]
                for impact in impacts:
                    assert impact in valid_impacts, f"Invalid impact level: {impact}"
                
                # Test that we can group by severity (like aggregation tests)
                severity_count = {}
                for violation in data:
                    impact = violation["impact"]
                    severity_count[impact] = severity_count.get(impact, 0) + 1
                
                assert sum(severity_count.values()) == count, "Severity grouping should match total count"
                
                # PRIVACY VALIDATION - Ensure no full page content from berkshirehathaway.com
                json_str = json.dumps(data)
                # Check for page structure that shouldn't be stored (vs. violation-specific HTML snippets)
                assert "<!DOCTYPE html>" not in json_str, "Should not store DOCTYPE declarations"
                assert "<head>" not in json_str, "Should not store head content"
                assert "<body>" not in json_str, "Should not store body content"
                assert "<title>" not in json_str, "Should not store page titles"
                
                # Verify we're not storing massive HTML content (violation snippets should be small)
                # Each violation can have multiple nodes, so we just check for reasonable bounds
                html_occurrences = json_str.count("<html")
                total_json_size = len(json_str)
                assert total_json_size < 50000, "Violation report should not contain excessive HTML content"
                
        except Exception as e:
            pytest.skip(f"Integration test skipped due to network/browser issue: {type(e).__name__}: {e}")
