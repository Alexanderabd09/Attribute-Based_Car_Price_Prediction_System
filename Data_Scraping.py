import time
import pandas as pd
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

#scraper did not work because they block ALL non-browser traffic with Cloudflare, TLS fingerprinting, bot detection, and JavaScript-rendered content.
#but code is here for reference

SEARCH_URL = "https://www.autotrader.co.uk/car-search?postcode=SW1A1AA&radius=1500"

def init_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1400,900")
    return uc.Chrome(options=options)


def scroll_page(driver, times=3):
    for _ in range(times):
        driver.execute_script("window.scrollBy(0, 1400);")
        time.sleep(1.5)


def parse_listing(card):
    try:
        title = card.find("h2", class_="product-card-details__title").text.strip()
    except:
        title = None

    try:
        price = card.find("span", class_="product-card-pricing__price").text.strip()
        price = price.replace("£", "").replace(",", "")
    except:
        price = None

    try:
        year = title.split()[0]
    except:
        year = None

    specs = card.find_all("li", class_="listing-key-specs__item")
    mileage, transmission, fuel_type = None, None, None

    for spec in specs:
        t = spec.text.strip()
        if "miles" in t:
            mileage = t.replace("miles", "").replace(",", "").strip()
        elif t in ["Manual", "Automatic"]:
            transmission = t
        elif t in ["Petrol", "Diesel", "Hybrid", "Electric"]:
            fuel_type = t

    try:
        location = card.find("div", class_="seller-town").text.strip()
    except:
        location = None

    return {
        "Title": title,
        "Year": year,
        "Price": price,
        "Mileage": mileage,
        "Transmission": transmission,
        "Fuel": fuel_type,
        "Location": location,
    }


def scrape_autotrader(pages=1):
    driver = init_driver()
    results = []

    for page in range(1, pages + 1):
        url = SEARCH_URL + f"&page={page}"
        print(f"Scraping page {page}: {url}")
        driver.get(url)
        time.sleep(4)

        scroll_page(driver, times=4)

        soup = BeautifulSoup(driver.page_source, "lxml")
        cards = soup.find_all("article", class_="product-card")

        print(f"Found {len(cards)} listings on this page.")

        for card in cards:
            data = parse_listing(card)
            results.append(data)

    driver.quit()
    return pd.DataFrame(results)



# RUN SCRAPER

df = scrape_autotrader(pages=3)  # scrape 3 pages
df.to_csv("autotrader_data.csv", index=False)

print(df.head())
print(f"\nSaved {len(df)} listings.")
