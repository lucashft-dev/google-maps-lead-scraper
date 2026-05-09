from playwright.sync_api import sync_playwright

from scraper import run_scraper
from config import targets, max_results


with sync_playwright() as playwright:

    browser = playwright.chromium.launch(headless=False)

    page = browser.new_page()

    run_scraper(page, targets, max_results)

    browser.close()