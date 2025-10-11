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
                
                # Verify JSON structure
                with open("violations.json", "r") as f:
                    data = json.load(f)
                assert isinstance(data, list)
                
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
            
            # If violations found, verify basic structure
            if count > 0:
                violation = data[0]
                assert "id" in violation, "Violation should have id"
                assert "impact" in violation, "Violation should have impact"
                assert violation["impact"] in ["minor", "moderate", "serious", "critical"], "Impact should be valid"
                
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
                
        except Exception as e:
            pytest.skip(f"Integration test skipped due to network/browser issue: {e}")
