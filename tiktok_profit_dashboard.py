# =============================================
# REAL-TIME TIKTOK SHOP FULL SCANNER (200+ PRODUCTS)
# Scans trending best-sellers live for customers
# Deploy on Streamlit Cloud for instant sharing
# =============================================

import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

st.set_page_config(page_title="Real-Time TikTok Shop Scanner", layout="wide")
st.title("Live TikTok Shop Best-Sellers Scanner")
st.markdown("### Scans 100+ trending products in real time – perfect for customers to find winners instantly")

# Sidebar for customer inputs
st.sidebar.image("https://i.imgur.com/4dZfP4G.png", width=200)  # Your logo here
st.sidebar.markdown("### Customize Your Scan")
num_products = st.sidebar.slider("Max products to scan (loads full list)", 50, 300, 150)
wholesale_cost = st.sidebar.number_input("Your wholesale cost ($)", 0.0, 50.0, 5.0)
fee_percent = st.sidebar.slider("TikTok fee % (2-8%)", 2, 10, 6) / 100
ad_cost = st.sidebar.number_input("Ad spend per sale ($)", 0.0, 20.0, 3.0)

@st.cache_data(ttl=1800)  # Cache for 30 mins – fresh scans each time
def scan_tiktok_shop(limit):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Official 2025 TikTok Shop ranking page for real-time trending products
    driver.get("https://ads.tiktok.com/business/creativecenter/top-products/pc/en?region=US")
    time.sleep(10)

    # Infinite scroll to load the FULL list (up to 200+ products)
    products_loaded = 0
    while products_loaded < limit:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for new products to load
        new_cards = driver.find_elements(By.CSS_SELECTOR, "div[data-e2e='product-card']")
        if len(new_cards) == products_loaded:
            break  # Stop if no more load
        products_loaded = len(new_cards)

    products = []
    cards = driver.find_elements(By.CSS_SELECTOR, "div[data-e2e='product-card']")[:limit]
    for i, card in enumerate(cards, 1):
        try:
            name = card.find_element(By.CSS_SELECTOR, "div[data-e2e='product-name'] span").text.strip()[:60]
            price_text = card.find_element(By.CSS_SELECTOR, "[data-e2e='product-price']").text.replace("$", "").strip()
            price = float(price_text) if price_text.replace(".", "").isdigit() else 0.0
            category = card.find_element(By.CSS_SELECTOR, "[data-e2e='product-category'] span").text.strip()
            sales = card.find_element(By.CSS_SELECTOR, "[data-e2e='sales-volume'] span").text.strip() if card.find_elements(By.CSS_SELECTOR, "[data-e2e='sales-volume'] span") else "Hot Trend"

            profit = price - wholesale_cost - (price * fee_percent) - ad_cost
            margin = (profit / price * 100) if price > 0 else 0

            products.append({
                "Rank": i,
                "Product": name,
                "Price": f"${price:.2f}",
                "Category": category,
                "Sales": sales,
                "Cost": f"${wholesale_cost:.2f}",
                "Profit": f"${profit:.2f}",
                "Margin": f"{margin:.1f}%",
                "Verdict": "🟢 WINNER" if margin >= 25 else "🟡 OK" if margin >= 15 else "🔴 Skip"
            })
        except:
            continue

    driver.quit()
    return pd.DataFrame(products)

if st.button("SCAN TIKTOK SHOP LIVE NOW", type="primary"):
    with st.spinner(f"Scanning up to {num_products} trending products in real time..."):
        df = scan_tiktok_shop(num_products)
    
    if not df.empty:
        st.success(f"Loaded {len(df)} real-time products from TikTok Shop!")
        
        # Color-coded table
        def color_verdict(val):
            color = {'🟢 WINNER': 'lightgreen', '🟡 OK': 'lightyellow', '🔴 Skip': 'lightcoral'}.get(val, 'white')
            return f'background-color: {color}'
        
        st.dataframe(df.style.applymap(color_verdict, subset=['Verdict']), height=700, use_container_width=True)
        
        csv = df.to_csv(index=False).encode()
        st.download_button("Download Full Scan as CSV", csv, "tiktok_shop_scan.csv")
    else:
        st.error("TikTok load failed this time – try again or lower max products.")

st.caption("Customer-ready tool • Real-time scans on demand • Sell as a subscription app")
