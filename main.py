from selenium import webdriver
from axe_selenium_python import Axe

def test_google():
    driver = webdriver.Firefox()
    driver.get("https://www.berkshirehathaway.com/")
    axe = Axe(driver)
    # Inject axe-core javascript into page.
    axe.inject()
    # Run axe accessibility checks.
    results = axe.run()
    # Write results to file
    axe.write_results(results["violations"], 'a11y.json')
    driver.close()

test_google()
