from playwright.sync_api import sync_playwright
import csv
import re 


targets = [
        "Restaurant Lyon",
        "Bar Lyon",
       ]

max_results = 10
# leads = []
seen = set()

duplicate_count = 0
missing_phone_count = 0
missing_website_count = 0


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

                print(f"Résultats : {current_count}")

                if current_count >= max_results:
                        print(f"Objectif atteint : {max_results}")
                        break

                if current_count == previous_count:
                        print(f"Plus de nouveaux résultats. {current_count} résultats trouvé.")
                        break

                previous_count = current_count

# Nettoyage des données pour les rendre exploitables
def clean_rating(rating):
    if rating == "N/A":
        return None
    return float(rating.split()[0].replace(",", "."))

def clean_reviews(reviews):
    if reviews == "N/A":
        return None
    return int(re.sub(r"[^\d]", "", reviews))

def clean_address(address):
    if address == "N/A":
        return None
    return " ".join(address.split()).replace("", "").strip()



with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()

        for target in targets:
                leads = []
                print("\n" + "=" * 50)
                print(f"🔎 Scraping: {target}")
                print("-" * 50)
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
                                missing_phone_count += 1


                        website_locator = container.locator("a[data-item-id='authority']")
                        if website_locator.count() > 0:  # Utilise count() car locator toujours présent (true)
                                website = website_locator.get_attribute("href")
                        else:
                                website = "N/A"
                                missing_website_count += 1


                        rating_locator = container.locator("span[aria-label*='étoiles']")
                        if rating_locator.count() > 0:
                                rating = rating_locator.first.get_attribute("aria-label")
                        else:
                                rating = "N/A"

                        # Pour le moment, récupérer le nombre d'avis fonctionne uniquement avec le headless de playwright en False
                        # Ce sera un des problèmes a corriger à l'avenir, pour le moment ça fonctionne en headless = True
                        reviews_locator = container.locator("span[role='img'][aria-label*='avis']")
                        if reviews_locator.count() > 0:
                                reviews = reviews_locator.first.get_attribute("aria-label")
                        else:
                                reviews = "N/A"
                        
                        address_locator = container.locator('button[data-item-id="address"]')
                        if address_locator.count() > 0:
                                address = address_locator.first.inner_text()
                                address = address.replace("\n", " ").replace("", "").strip() # Obliger pour un rendu propre
                        else:
                                address = "N/A"


                        # Ici je viens éviter les doublons en sortant de la boucle si deja présent dans seen
                        # Et j'ajoute un compteur pour les doublons
                        key = f"{name}-{phone}"
                        if key in seen:
                               duplicate_count += 1
                               continue
                        seen.add(key)

                        lead = {
                        "target": target,
                        "name": name,
                        "phone": phone,
                        "website": website,
                        "rating": clean_rating(rating),
                        "reviews": clean_reviews(reviews),
                        "address": clean_address(address)
                        }

                        leads.append(lead)

                        # Maintenant on va créer un fichier .csv pour chaque target, donc export dans la boucle
                filename = target.lower().replace(" ", "_") + ".csv"
                with open(filename, mode="w", newline="", encoding="utf-8") as file:
                        writer = csv.DictWriter(
                               file,
                               fieldnames=["target", "name", "phone", "website", "rating", "reviews", "address"]
                               )
                        writer.writeheader()
                        writer.writerows(leads)
                        
                print("\n📊 Stats:")
                print(f"- Leads: {len(leads)}")
                print(f"- Doublons: {duplicate_count}")
                print(f"- Sans téléphone: {missing_phone_count}")
                print(f"- Sans site web: {missing_website_count}")
                print(f"\n💾 File: {filename}")


# with open("leads.csv", mode="w", newline="", encoding="utf-8") as file:
#       writer = csv.DictWriter(
#             file,
#             fieldnames=["target", "name", "phone", "website", "rating", "reviews", "address"]
#       )
#       writer.writeheader()
#       writer.writerows(leads)


# print(70 * "_")
# print(f"Extraction terminée, {len(leads)} leads enregistrés dans leads.csv")
# print(f"[INFO] {len(leads)} leads enregistrés")
# print(f"[INFO] {duplicate_count} doublons ignorés")
# print(f"[INFO] {missing_phone_count} sans téléphone")
# print(f"[INFO] {missing_website_count} sans site web")