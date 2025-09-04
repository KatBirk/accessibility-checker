from playwright.sync_api import sync_playwright
from axe_core_python.sync_playwright import Axe

axe = Axe()

with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.goto("https://www.berkshirehathaway.com/")
    result = axe.run(page)
    browser.close()

violations = result['violations']
print(f"{len(violations)} violations found.")
