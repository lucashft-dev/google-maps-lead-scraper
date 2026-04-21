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

# On recupère les noms seulement si ce n'est pas sponsorisé
def extract_name(item):
    lines = item.inner_text().split("\n")
    lines = [l.strip() for l in lines if l.strip()]
    if "Sponsorisé" in lines:
        return None
    
    return lines[0]



with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.google.com/maps")
        accept_cookie(page)
        search_target(page)
        results = page.locator("div[role='article']")
        for i in range(results.count()):
            item = results.nth(i)
            name = extract_name(item)
            if name:
                print(name)