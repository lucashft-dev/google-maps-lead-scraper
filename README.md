# Google Maps Leads Scraper

A Python automation tool built with Playwright to scrape business leads directly from Google Maps.

This project was designed to simulate a real-world freelance lead generation tool by extracting useful business information such as phone numbers, websites, ratings, reviews, and addresses.  
The goal is to automate local business prospecting workflows and export clean, structured CSV datasets that can be used for outreach, market research, or lead generation services.

---

# ✨ Features

- 🔎 Multi-target scraping
- ♾️ Infinite scroll support
- 🚫 Duplicate filtering
- 📁 CSV export by target
- ⭐ Rating extraction
- 📝 Reviews extraction
- 📍 Address extraction
- 🧹 Cleaned data output
- 🧩 Modular project structure

---

# 🛠️ Tech Stack

- 🐍 Python
- 🎭 Playwright
- 📄 CSV
- 🔤 Regex

---

# 📂 Project Structure

```text
gmaps_leads_scraper/
│
├── main.py
├── scraper.py
├── utils.py
├── config.py
├── requirements.txt
├── README.md
│
├── data/
│
├── pre-refactor/
│   └── old-scraper.py
```

---

# ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/lucashft-dev/google-maps-lead-scraper
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install Playwright browser:

```bash
playwright install
```

---

# 🔧 Configuration

Edit targets and max results inside `config.py`

```python
targets = [
    "Target 1",
    "Target 2",
]

max_results = 20
```

---

# 🚀 Usage

Run the scraper:

```bash
python main.py
```

---

# 📤 Output

CSV files are automatically generated inside the `data/` folder.

Example:

```text
data/
├── Target1.csv
├── Target2.csv
```

Example output:

| name | phone | website | rating | reviews |
|---|---|---|---|---|
| Contrast. | 0465845121 | https://contrast-bar.com | 5.0 | 401 |

---

# ⚠️ Current Limitations

- Reviews extraction currently works reliably with `headless=False`
- Google Maps DOM structure may change over time

---

# 🔮 Future Improvements

- 📧 Email extraction from websites
- 🤖 Better headless support
- 🖥️ CLI arguments
- 🌐 Proxy support
- ⚡ Async version

---

# 📜 Disclaimer

This project is for educational purposes only.

Users are responsible for respecting Google Maps Terms of Service and local regulations regarding data collection and usage.