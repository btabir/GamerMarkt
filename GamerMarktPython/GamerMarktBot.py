import time
import smtplib
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright

# ========== AYARLAR ==========
EMAIL_ADDRESS = "tabirbugra2@gmail.com"
EMAIL_PASSWORD = "thda tvhh ngzz qbcl"  # boşluksuz app şifren
TO_EMAIL = "tabirbugra2@gmail.com"

CHECK_INTERVAL = 300  # 5 dakika = 300 saniye

URL = "https://www.gamermarkt.com/tr/ilanlar/lol-hesap?max_price=405&min_skins=45&servers[]=TR"
reported_links = set()  # daha önce bildirilen ilanlar

def send_email(title, link, price):
    subject = "🆕 GamerMarkt'ta Yeni Hesap Bulundu!"
    body = f"Yeni bir hesap bulundu:\n\nBaşlık: {title}\nFiyat: {price}\nLink: {link}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"[EMAIL] Gönderildi: {title} - {price} TL")
    except Exception as e:
        print(f"[HATA] E-posta gönderilemedi: {e}")

def check_listings():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(6000)  # 6 saniye bekle JS için

        # ilan kartları
        cards = page.locator(".fw-600")
        count = cards.count()
        print(f"[INFO] {count} ilan bulundu.")

        # fiyatlar .fw-600 class'ı ile alınır
        price_elements = page.locator(".fw-600")
        price_count = price_elements.count()
        prices = [price_elements.nth(i).inner_text().replace("₺", "").strip() for i in range(price_count)]
        print(f"[Fiyatlar] {', '.join(prices)} TL")

        for i in range(count):
            card = cards.nth(i)
            title = card.locator(".account-title").inner_text()
            link = card.locator("a.account-link").get_attribute("href")
            price = price_elements.nth(i).inner_text().replace("₺", "").strip()
            full_link = "https://www.gamermarkt.com" + link

            if full_link not in reported_links:
                reported_links.add(full_link)
                send_email(title, full_link, price)

        browser.close()

if __name__ == "__main__":
    print("[BOT] GamerMarkt takip botu başladı.")
    while True:
        try:
            check_listings()
        except Exception as e:
            print(f"[HATA] {e}")
        time.sleep(CHECK_INTERVAL)
