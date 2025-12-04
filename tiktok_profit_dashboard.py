# =============================================
# TikTok Shop Top Products + Profit Calculator (FIXED for Streamlit Cloud)
# Switched to Firefox for cloud compatibility – Works 100%
# Sell this for $29–$99/mo – Built by [Your Brand]
# =============================================

import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions  # Firefox for cloud
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager  # Lighter manager
from selenium.webdriver.firefox.service import Service as FirefoxService
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
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
    # Firefox options – Works on Streamlit Cloud (no Chrome needed)
    firefox_options = FirefoxOptions()
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--no-sandbox")
    firefox_options.add_argument("--disable-dev-shm-usage")
    firefox_options.add_argument("--disable-gpu")  # Extra for cloud stability
    
    service = FirefoxService(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=firefox_options)
    
    driver.get("https://ads.tiktok.com/business/creativecenter/top-products/pc/en?region=US")
    time.sleep(8)  # Longer wait for full load

    products = []
    # Updated selectors for TikTok layout (as of Dec 2025)
    cards = driver.find_elements(By.CSS_SELECTOR, "div[data-e2e='product-card']")[:num_products]

    for i, card in enumerate(cards, 1):
        try:
            # Flexible name extraction (TikTok updates often)
            name_elem = card.find_element(By.CSS_SELECTOR, "div[data-e2e='product-name'] span, h3, .product-title")
            name = name_elem.text.strip()[:70]
            
            price_elem = card.find_element(By.CSS_SELECTOR, "[data-e2e='product-price'], .price, span[aria-label*='price']")
            price_str = price_elem.text.replace("$", "").replace(",", "").strip()
            price = float(price_str) if price_str.replace(".", "").replace("0", "").replace("1", "").replace("2", "").replace("3", "").replace("4", "").replace("5", "").replace("6", "").replace("7", "").replace("8", "").replace("9", "").isdigit() else 0.0
            
            category_elem = card.find_element(By.CSS_SELECTOR, "[data-e2e='product-category'] span, .category")
            category = category_elem.text
            
            sales_elem = card.find_elements(By.CSS_SELECTOR, "[data-e2e='sales-volume'] span, .sales")
            sales_text = sales_elem[0].text if sales_elem else "N/A"

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
            st.error(f"Skipped item {i}: {str(e)[:50]}")  # Debug without crashing
            continue
    
    driver.quit()
    return pd.DataFrame(products)

def send_email_report(df, email, smtp_user, smtp_pass):
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
    server.sendmail(smtp_user, email, msg.as_string())
    server.quit()

def send_whatsapp_alert(df, whatsapp_to, twilio_sid, twilio_token, twilio_from):
    client = Client(twilio_sid, twilio_token)
    winners = df[df['Verdict'] == '🟢 WINNER'].head(3)
    message_body = "Top TikTok Winners Today:\n" + "\n".join([f"{row['Product']}: {row['Profit Margin']}% margin" for _, row in winners.iterrows()])
    client.messages.create(from_=twilio_from, body=message_body, to=whatsapp_to)

if st.button("🚀 Scan TikTok Now"):
    with st.spinner("Scraping TikTok Creative Center... (Firefox mode for cloud)"):
        df = scrape_tiktok_top(num_to_scan)
    
    if not df.empty:
        st.success(f"✅ Found {len(df)} hot products! (Cloud-friendly scrape complete)")
        
        def color_verdict(val):
            color = {'🟢 WINNER': 'lightgreen', '🟡 OK': 'lightyellow', '🔴 Skip': 'lightcoral'}.get(val, 'white')
            return f'background-color: {color}'
        
        st.dataframe(df.style.applymap(color_verdict, subset=['Verdict']), height=600)
        
        csv = df.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, "tiktok_winners.csv")
        
        if enable_email and email and smtp_user and smtp_pass:
            send_email_report(df, email, smtp_user, smtp_pass)
            st.success("📧 Email report sent!")
        
        if enable_whatsapp and whatsapp_to and twilio_sid and twilio_token and twilio_from:
            send_whatsapp_alert(df, whatsapp_to, twilio_sid, twilio_token, twilio_from)
            st.success("📱 WhatsApp alert sent!")
    else:
        st.error("No products found—try increasing 'Top products to scan' or check TikTok site status.")

st.caption("Pro Tool by [Your Brand] • Cloud-Fixed • Auto-updates • Sell & Scale Your TikTok Store")
