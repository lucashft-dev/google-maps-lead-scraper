from utils import clean_rating, clean_reviews, clean_address
import csv


seen = set()


def accept_cookie(page):
        cookie_button = page.get_by_role("button", name="Tout accepter")
        if cookie_button.is_visible(timeout=3000):
                cookie_button.click()
        else:
            print("Bouton cookie non trouver")

def search_target(page, target):
    search_box = page.get_by_role("combobox")
    search_box.click()
    search_box.fill(target)
    page.locator("button[aria-label='Rechercher']").click()
    page.locator("div[role ='article']").first.wait_for(state="visible")

# On recupère les noms seulement si ce n'est pas sponsorisé
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


def run_scraper(page, targets, max_results):

        for target in targets:

                leads = []

                duplicate_count = 0
                missing_phone_count = 0
                missing_website_count = 0

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
                        # Utilise count() car locator toujours présent (true)
                        if website_locator.count() > 0:
                                website = website_locator.get_attribute("href")
                        else:
                                website = "N/A"
                                missing_website_count += 1


                        rating_locator = container.locator("span[aria-label*='étoiles']")
                        if rating_locator.count() > 0:
                                rating = rating_locator.first.get_attribute("aria-label")
                        else:
                                rating = "N/A"

                        # Pour le moment, récupérer le nombre d'avis fonctionne
                        # uniquement avec le headless de playwright en False
                        reviews_locator = container.locator("span[role='img'][aria-label*='avis']")
                        if reviews_locator.count() > 0:
                                reviews = reviews_locator.first.get_attribute("aria-label")
                        else:
                                reviews = "N/A"


                        address_locator = container.locator('button[data-item-id="address"]')
                        if address_locator.count() > 0:
                                address = address_locator.first.inner_text()
                                # Obligé pour un rendu propre
                                address = address.replace("\n", " ").replace("", "").strip()
                        else:
                                address = "N/A"

                        # Ici je viens éviter les doublons en sortant
                        # de la boucle si deja présent dans seen
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

                # Maintenant on va créer un fichier .csv
                # pour chaque target
                filename = f"data/{target.lower().replace(' ', '_')}.csv"

                with open(filename, mode="w", newline="", encoding="utf-8") as file:
                        writer = csv.DictWriter(
                               file,
                               fieldnames=[
                                       "target",
                                       "name",
                                       "phone",
                                       "website",
                                       "rating",
                                       "reviews",
                                       "address"
                               ]
                        )
                        writer.writeheader()
                        writer.writerows(leads)


                print("\n📊 Stats:")
                print(f"- Leads: {len(leads)}")
                print(f"- Doublons: {duplicate_count}")
                print(f"- Sans téléphone: {missing_phone_count}")
                print(f"- Sans site web: {missing_website_count}")

                print(f"\n💾 File: {filename}")