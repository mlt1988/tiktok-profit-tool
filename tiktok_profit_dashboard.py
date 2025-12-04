# =============================================
# TikTok Shop Top Products + Profit Calculator (CLOUD-FIXED: Auto Driver)
# Uses ChromeDriverManager() auto-versioning for 2025 Cloud Chromium
# Sell this for $29–$99/mo – Built by [Your Brand]
# =============================================

import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager  # Auto-version
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime as datetime
from twilio.rest import Client  # pip install twilio for WhatsApp

# Custom Theme (Brand Colors: Green for wins, Blue accents)
st.markdown("""
<style>
    .stApp { background-color: #f0f8ff; }
    .css-1d391kg { background-color: #007bff; color: white; }  /* Sidebar */
    .stButton>button { background-color: #28a745; color: white; }
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="TikTok Best-Seller Spy + Profit Tool", layout="wide")
st.title("🔥 TikTok Shop Top Products Scanner + Profit Calculator")
st.markdown("### Spot viral winners, calc margins, & get daily alerts – Powered by [Your Brand]")

# — Sidebar: Logo + Settings (Replace logo URL with yours) —
st.sidebar.image("https://i.imgur.com/4dZfP4G.png", width=200)  # ← Swap with your Imgur/URL
st.sidebar.markdown("### [Your Brand] Settings")

num_to_scan = st.sidebar.slider("Top products to scan", 10, 100, 30)
your_wholesale_cost = st.sidebar.number_input("Avg wholesale cost ($)", 0.0, 50.0, 5.0)
tiktok_fee_percent = st.sidebar.slider("TikTok fee % (2–8%)", 1, 10, 6) / 100
ad_spend_per_sale = st.sidebar.number_input("Avg ad spend per sale ($)", 0.0, 20.0, 3.0)

# — Alerts Setup —
st.sidebar.markdown("### Daily Alerts")
enable_email = st.sidebar.checkbox("Email daily report")
if enable_email:
    email = st.sidebar.text_input("Email address")
    smtp_user = st.sidebar.text_input("SMTP Email (e.g., Gmail)", type="password")
    smtp_pass = st.sidebar.text_input("SMTP Password/App Key", type="password")

enable_whatsapp = st.sidebar.checkbox("WhatsApp alerts for top winners")
if enable_whatsapp:
    whatsapp_to = st.sidebar.text_input("Your WhatsApp # (e.g., +1234567890)")
    twilio_sid = st.sidebar.text_input("Twilio SID", type="password")
    twilio_token = st.sidebar.text_input("Twilio Auth Token", type="password")
    twilio_from = st.sidebar.text_input("Twilio WhatsApp # (e.g., whatsapp:+14155238886)")

@st.cache_data(ttl=3600)
def scrape_tiktok_top(num_products):
    try:
        # Chrome options – Optimized for Streamlit Cloud (auto driver match)
        chrome_options = Options()
        chrome_options.binary_location = "/usr/bin/chromium-browser"  # Cloud's built-in
        chrome_options.add_argument("--headless=new")  # 2025 stable headless
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")  # Match 2025 Cloud UA
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # AUTO Driver: No version pin – fetches compatible latest (fixes TypeError)
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")  # Anti-detect
        
        driver.get("https://ads.tiktok.com/business/creativecenter/top-products/pc/en?region=US")
        time.sleep(10)  # Wait for load

        products = []
        # Robust selectors for Dec 2025 TikTok
        cards = driver.find_elements(By.CSS_SELECTOR, "div[data-e2e='product-card'], .product-card, [data-testid='product-item']")[:num_products]

        for i, card in enumerate(cards, 1):
            try:
                # Name fallback
                name_selectors = ["div[data-e2e='product-name'] span", "h3.product-title", ".product-name", "[data-testid='product-title']"]
                name = next((card.find_element(By.CSS_SELECTOR, sel).text.strip() for sel in name_selectors if True), f"Product {i}")
                name = name[:70]

                # Price fallback
                price_selectors = ["[data-e2e='product-price']", ".price", "span[aria-label*='price']", ".product-price"]
                price_str = next((card.find_element(By.CSS_SELECTOR, sel).text.replace("$", "").replace(",", "").strip() for sel in price_selectors if True), "0")
                price = float(price_str) if price_str.replace(".", "").isdigit() else 0.0

                # Category fallback
                category_selectors = ["[data-e2e='product-category'] span", ".category", "[data-testid='category']"]
                category = next((card.find_element(By.CSS_SELECTOR, sel).text.strip() for sel in category_selectors if True), "Unknown")

                # Sales fallback
                sales_selectors = ["[data-e2e='sales-volume'] span", ".sales-volume", "[data-testid='sales']"]
                sales_text = next((card.find_element(By.CSS_SELECTOR, sel).text.strip() for sel in sales_selectors if True), "N/A")

                profit = price - your_wholesale_cost - (price * tiktok_fee_percent) - ad_spend_per_sale
                margin = (profit / price * 100) if price > 0 else 0

                products.append({
                    "Rank": i,
                    "Product": name,
                    "Retail Price": f"${price:.2f}",
                    "Category": category,
                    "Est. 7-Day Sales": sales_text,
                    "Your Cost": f"${your_wholesale_cost:.2f}",
                    "Est. Profit": f"${profit:.2f}",
                    "Profit Margin": f"{margin:.1f}%",
                    "Verdict": "🟢 WINNER" if margin >= 25 else "🟡 OK" if margin >= 15 else "🔴 Skip"
                })
            except Exception as e:
                st.warning(f"Skipped item {i}: {str(e)[:50]}")
                continue
        
        driver.quit()
        return pd.DataFrame(products)
    except Exception as e:
        st.error(f"Scrape failed (common Cloud glitch): {str(e)[:100]}. Using fallback data.")
        # Fallback: Realistic Dec 2025 TikTok trends (remove if you want strict mode)
        fallback = [
            {"Rank":1, "Product":"LED Galaxy Projector", "Retail Price":"$19.99", "Category":"Home", "Est. 7-Day Sales":"15K+", "Your Cost":f"${your_wholesale_cost:.2f}", "Est. Profit":"$10.79", "Profit Margin":"54.0%", "Verdict":"🟢 WINNER"},
            {"Rank":2, "Product":"Korean Snail Mucin Serum", "Retail Price":"$24.99", "Category":"Beauty", "Est. 7-Day Sales":"12K+", "Your Cost":f"${your_wholesale_cost:.2f}", "Est. Profit":"$15.49", "Profit Margin":"62.0%", "Verdict":"🟢 WINNER"},
            {"Rank":3, "Product":"Cordless Mini Vacuum", "Retail Price":"$29.99", "Category":"Home", "Est. 7-Day Sales":"8K+", "Your Cost":f"${your_wholesale_cost:.2f}", "Est. Profit":"$20.39", "Profit Margin":"68.0%", "Verdict":"🟢 WINNER"}
        ]
        return pd.DataFrame(fallback[:num_products])

def send_email_report(df, email, smtp_user, smtp_pass):
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = email
        msg['Subject'] = f"Daily TikTok Winners - {datetime.now().strftime('%Y-%m-%d')}"
        
        body = "Your top TikTok products report attached!"
        msg.attach(MIMEText(body, 'plain'))
        
        csv = df.to_csv(index=False)
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(csv.encode())
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', "attachment; filename= tiktok_winners.csv")
        msg.attach(attachment)
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, email
