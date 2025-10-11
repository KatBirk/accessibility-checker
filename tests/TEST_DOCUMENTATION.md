# Test Documentation

## What Are We Testing?

- **Scanning websites** for accessibility issues (unit, functional, and integration approaches)
- **Saving results** to JSON files properly  
- **Counting violations** across multiple pages
- **Handling errors** like timeouts and bad URLs
- **Server functionality** for displaying reports
- **User interface logic** like URL selection and progress tracking

---

## How to Run Tests

Run from the `accessibility-checker` directory:

```bash
# Run all tests (7 tests, ~20 seconds)
pytest tests/ -v

# Run only fast unit tests (2 tests, ~1 second)
pytest tests/test_unit.py -v

# Run only functional tests (2 tests, ~1 second)  
pytest tests/test_functional.py -v

# Run only integration tests (3 tests, ~20 seconds - requires internet)
pytest tests/test_integration.py -v

# Run with coverage report
pytest tests/ --cov=main --cov-report=html
```

**If the above doesn't work**, try these alternatives:
```bash
# Using python -m pytest
python -m pytest tests/ -v

# Or with specific Python path like this
C:/Python312/python.exe -m pytest tests/ -v
```

---

## test_unit.py - Unit Tests (2 tests)

**Fast, isolated tests using mocks - only test pure functions that exist**

### `TestBasicFunctions` (2 tests)
* `test_testWebsite_returns_violation_count`: Tests that `testWebsite()` returns integer violation count with mocked playwright
* `test_start_server_creates_http_server`: Tests that `start_server()` creates HTTP server on specified port

---

## test_functional.py - Functional Tests (2 tests)

**Real functions with mocked dependencies - test actual main.py logic**

### `TestMainFunctions` (2 tests)
* `test_testWebsite_full_workflow`: Tests complete `testWebsite()` workflow with mocked playwright, verifies browser lifecycle, JSON output, and violation structure
* `test_start_progress_workflow_integration`: Tests the complete `start_progress()` function workflow - sitemap fetching, URL processing, violation aggregation, and GUI updates

---

## test_integration.py - Integration Tests (3 tests)

**Real browser automation with actual network calls - end-to-end testing**

### `TestCompleteWorkflows` (1 test)
* `test_sitemap_to_violations_pipeline`: Tests complete pipeline from sitemap parsing to violation aggregation to JSON output

### `TestRealBrowserIntegration` (2 tests)
* `test_real_browser_scan_reliable_page`: Full browser automation scanning reliable website (playwright.dev)
* `test_real_browser_scan_complex_page`: Tests complex page with potential accessibility issues (berkshirehathaway.com)

**Note**: Integration tests require internet connection and take longer
