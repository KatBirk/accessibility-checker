from playwright.sync_api import sync_playwright
from axe_core_python.sync_playwright import Axe
import json

axe = Axe()
urls = [
    "https://www.google.com/",
    "https://www.berkshirehathaway.com/",
    "https://www.microsoft.com/",
    "https://www.playwright.dev/",
    "https://www.op.europa.eu/en/web/webguide/",
    "https://www.github.com/",
    "https://www.wikipedia.org/"
]

def testWebsite(url):
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch()
        page = browser.new_page()
        page.goto("https://www.berkshirehathaway.com/")
        results = axe.run(page)
        browser.close()
        violations = results["violations"]
        with open('violations.json', 'w') as f:
            json.dump(violations, f, indent=4)


for i in range(len(urls)):
    testWebsite(i)

print(f"{len(violations)} violations found.")
