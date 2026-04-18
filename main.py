from playwright.sync_api import sync_playwright

def accept_cookie(page):
        cookie_button = page.get_by_role("button", name="Tout accepter")
        if cookie_button.is_visible(timeout=3000):
                cookie_button.click()
        else:
            print("Bouton cookie non trouver")

# J'ai nommé 'target' car on peut chercher n'importe quel type de leads
def search_target(page):
    search_box = page.get_by_role("combobox")
    search_box.click()
    search_box.fill("Restaurant Lyon")
    page.locator("button[aria-label='Rechercher']").click()
    page.locator("div[role ='article']").first.wait_for(state="visible")


with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.google.com/maps")
        accept_cookie(page)
        search_target(page)
        results = page.locator("div[role='article']")
        page.pause()