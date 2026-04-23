from playwright.sync_api import sync_playwright
import csv


target = "Restaurant Lyon"
leads = []


def accept_cookie(page):
        cookie_button = page.get_by_role("button", name="Tout accepter")
        if cookie_button.is_visible(timeout=3000):
                cookie_button.click()
        else:
            print("Bouton cookie non trouver")

# J'ai nommé 'target' car on peut chercher n'importe quel type de leads
# Target défini en haut du script
def search_target(page):
    search_box = page.get_by_role("combobox")
    search_box.click()
    search_box.fill(target)
    page.locator("button[aria-label='Rechercher']").click()
    page.locator("div[role ='article']").first.wait_for(state="visible")

# On recupère les noms seulement si ce n'est pas sponsorisé
# Sert aussi maintenant a filtrer avant de cliquer sur fiche élément
# On garde que les résultats non sponsorisés
def extract_name(item):
    lines = item.inner_text().split("\n")
    lines = [l.strip() for l in lines if l.strip()]
    if "Sponsorisé" in lines:
        return None
    
    return lines[0]

# Je l'ai défini de base a 5 mais a augmenter en fontion du besoin
def infinite_scroll(page):
        for _ in range(5):
                page.evaluate("""
                        () => {
                                const feed = document.querySelector("div[role='feed']");
                                if (feed) {
                                feed.scrollTop = feed.scrollHeight;
                                }
                        }
                        """)
                page.wait_for_timeout(2000)



with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.google.com/maps")
        accept_cookie(page)
        search_target(page)
        infinite_scroll(page)

        results = page.locator("div[role='article']")

        for i in range(results.count()):
                item = results.nth(i)
                valid_item = extract_name(item)
                if not valid_item:
                    continue
                item.click()
                page.wait_for_timeout(2000)

                container = page.locator("div[role='main']").last # .last car on cible la fenetre container qui doit charger, logiquement ce sera la dernière

                name = container.get_attribute("aria-label")

                phone_raw = container.locator("button[data-item-id*='phone']").get_attribute("data-item-id")
                if phone_raw:
                        phone = phone_raw.split(":")[-1]
                else:
                        phone = "N/A"

                website_locator = container.locator("a[data-item-id='authority']")
                if website_locator.count() > 0:  # Utilise count() car locator toujours présent
                        website = website_locator.get_attribute("href")
                else:
                        website = "N/A"

                lead = {
                      "name": name,
                      "phone": phone,
                      "website": website
                }

                leads.append(lead)
        
        # print(leads) ---> Inutile dans la version actuel car résulat récupérer en CSV, garder pour debug 

with open("leads.csv", mode="w", newline="", encoding="utf-8") as file:
      writer = csv.DictWriter(
            file,
            fieldnames=["name", "phone", "website"]
      )
      writer.writeheader()
      writer.writerows(leads)