from playwright.sync_api import sync_playwright
import csv


targets = [
       "Restaurant Lyon",
       "Bar Lyon"
       ]
max_results = 20
leads = []


def accept_cookie(page):
        cookie_button = page.get_by_role("button", name="Tout accepter")
        if cookie_button.is_visible(timeout=3000):
                cookie_button.click()
        else:
            print("Bouton cookie non trouver")

# J'ai nommé 'target' car on peut chercher n'importe quel type de leads
# Target défini en haut du script
def search_target(page, target):
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

# Scroll jusqu'à atteindre le nombre de résultat voulu ou jusqu'à ce qu'il n'y ait plus de nouveaux résultats
def infinite_scroll(page, max_results):
        feed = page.locator("div[role='feed']")
    
        previous_count = 0
        while True:
                page.evaluate("""
                        () => {
                                const feed = document.querySelector("div[role='feed']");
                                if (feed) {
                                feed.scrollTop = feed.scrollHeight;
                                }
                        }
                        """)
                page.wait_for_timeout(2000)

                results = page.locator("div[role='article']")
                current_count = results.count()

                print(f"Résultats actuel : {current_count}")

                if current_count >= max_results:
                        print(50 * "-")
                        print(f"Objectif atteint : {max_results} résultats")
                        break

                if current_count == previous_count:
                        print(50 * "-")
                        print(f"Plus de nouveaux résultats. {current_count} résultats trouvé.")
                        break

                previous_count = current_count



with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        for target in targets:
                print(50 * "_")
                print(f"Scraping en cours pour {target}.")
                page.goto("https://www.google.com/maps")
                accept_cookie(page)
                search_target(page, target)
                infinite_scroll(page, max_results)

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

                        phone_locator = container.locator("button[data-item-id*='phone']")
                        if phone_locator.count() > 0:
                                phone_raw = phone_locator.first.get_attribute("data-item-id")
                                phone = phone_raw.split(":")[-1] if phone_raw else "N/A"
                        else:
                                phone = "N/A"

                        website_locator = container.locator("a[data-item-id='authority']")
                        if website_locator.count() > 0:  # Utilise count() car locator toujours présent (true)
                                website = website_locator.get_attribute("href")
                        else:
                                website = "N/A"

                        lead = {
                        "target": target,
                        "name": name,
                        "phone": phone,
                        "website": website
                        }

                        leads.append(lead)


with open("leads.csv", mode="w", newline="", encoding="utf-8") as file:
      writer = csv.DictWriter(
            file,
            fieldnames=["target", "name", "phone", "website"]
      )
      writer.writeheader()
      writer.writerows(leads)


print(70 * "_")
print(f"Extraction terminée, {len(leads)} leads enregistrés dans leads.csv")