from playwright.sync_api import sync_playwright
from axe_core_python.sync_playwright import Axe
import json

axe = Axe()

with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.goto("https://www.berkshirehathaway.com/")
    results = axe.run(page)
    browser.close()
    violations = results["violations"]
    with open('violations.json'.json', 'w') as f:
        json.dump(violations, f, indent=4)


print(f"{len(violations)} violations found.")
