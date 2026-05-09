import re


# Nettoyage des données pour les rendre exploitables et plus facile a traiter 

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