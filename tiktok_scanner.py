import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

st.set_page_config(page_title="TikTok Winners", layout="wide")
st.title("TikTok Shop Live Scanner — 170+ Real Products")
st.markdown("Click the button → gets fresh trending products instantly")

# Settings
num = st.sidebar.slider("How many products", 50, 250, 150)
cost = st.sidebar.number_input("Your wholesale cost ($)", 0.0, 50.0, 5.0)
fee = st.sidebar.slider("TikTok fee %", 2, 10, 6) / 100
ads = st.sidebar.number_input("Ad spend per sale ($)", 0.0, 20.0, 3.0)

@st.cache_data(ttl=1800)
def scan_tiktok():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)   # uses the system driver from packages.txt

    driver.get("https://ads.tiktok.com/business/creativecenter/top-products/pc/en?region=US")
    time.sleep(10)

    # Load 150–200+ products
    for _ in range(20):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    cards = driver.find_elements(By.CSS_SELECTOR, "div[data-e2e='product-card']")[:num]
    data = []

    for i, card in enumerate(cards, 1):
        try:
            name = card.find_element(By.CSS_SELECTOR, "div[data-e2e='product-name'] span").text.strip()[:70]
            price = float(card.find_element(By.CSS_SELECTOR, "[data-e2e='product-price']").text.replace("$",""))
            cat = card.find_element(By.CSS_SELECTOR, "[data-e2e='product-category'] span").text
            sales = card.find_element(By.CSS_SELECTOR, "[data-e2e='sales-volume'] span").text if card.find_elements(By.CSS_SELECTOR, "[data-e2e='sales-volume'] span") else "Hot"

            profit = price - cost - (price * fee) - ads
            margin = round((profit / price) * 100, 1) if price > 0 else 0

            data.append({
                "Rank": i,
                "Product": name,
                "Price": f"${price:.2f}",
                "Category": cat,
                "Sales": sales,
                "Profit": f"${profit:.2f}",
                "Margin": f"{margin}%",
                "Verdict": "WINNER" if margin >= 25 else "OK"
            })
        except:
            continue

    driver.quit()
    return pd.DataFrame(data)

if st.button("SCAN TIKTOK LIVE NOW", type="primary"):
    with st.spinner("Loading real products…"):
        df = scan_tiktok()
    st.success(f"Loaded {len(df)} real trending products!")
    st.dataframe(df.style.applymap(lambda x: "background-color: #d4edda" if x=="WINNER" else "", subset=["Verdict"]), use_container_width=True)
    st.download_button("Download CSV", df.to_csv(index=False).encode(), "tiktok_winners.csv")
