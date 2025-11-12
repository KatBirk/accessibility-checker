# Test Documentation

- **Scanning websites** for accessibility issues (unit, functional, and integration approaches)
- **Saving results** to JSON files properly  
- **Counting violations** across multiple pages
- **Privacy-by-design compliance** ensuring no sensitive page content is stored
- **Server functionality** for displaying reports
- **End-to-end sitemap discovery to violation reporting** workflows

---

## How to Run Tests

Run from the `accessibility-checker` directory:

```bash
# Run all tests (6 tests, ~20 seconds)
pytest tests/ -v

# Using python -m pytest
python -m pytest tests/ -v

# Run only fast unit tests
pytest tests/test_unit.py -v

# Run only functional tests
pytest tests/test_functional.py -v

# Run only integration tests (3 tests, ~20 seconds - requires internet)
pytest tests/test_integration.py -v

# Run with coverage report
pytest tests/ --cov=main --cov-report=html
```

**If the above doesn't work**, try specific Python path:
```bash
C:/Python312/python.exe -m pytest tests/ -v
```

---

## test_unit.py - Unit Tests (2 tests)

**Fast, isolated tests using mocks - only test pure functions that exist**

### `TestBasicFunctions` (2 tests)
* `test_testWebsite_returns_violation_count`: Tests that `testWebsite()` returns integer violation count with mocked playwright
* `test_start_server_creates_http_server`: Tests that `start_server()` creates HTTP server on specified port

---

## test_functional.py - Functional Tests (1 test)

### `TestMainFunctions` (1 test)
* `test_testWebsite_full_workflow`: Tests complete `testWebsite()` workflow with mocked playwright, verifies browser lifecycle, JSON output, violation structure, and privacy compliance that ensures no sensitive page content is stored in violation reports

---

## test_integration.py - Integration Tests (3 tests)

**Real browser automation with network calls - end-to-end testing**

### `TestCompleteWorkflows` (1 test)
* `test_sitemap_to_violations_pipeline`: Tests complete pipeline from sitemap parsing to violation aggregation to JSON output, with privacy validation

### `TestRealBrowserIntegration` (2 tests)
* `test_real_browser_scan_reliable_page`: Full browser automation scanning reliable website (playwright.dev), with privacy compliance checks
* `test_real_browser_scan_complex_page`: Tests complex page with potential accessibility issues (berkshirehathaway.com)

**Note**: Integration tests require internet connection and take longer
