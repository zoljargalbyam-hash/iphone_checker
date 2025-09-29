from flask import Flask
import smtplib, requests, json, os

app = Flask(__name__)

# ============================
# SETTINGS
# ============================
ZIP_CODE = os.getenv("ZIP_CODE", "22204")
PRODUCT_ID = os.getenv("PRODUCT_ID", "MFXH4LL/A")
EMAIL_FROM = os.getenv("EMAIL_FROM", "")
EMAIL_TO = os.getenv("EMAIL_TO", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

def check_availability_and_notify():
    url = f"https://www.apple.com/shop/retail/pickup-message?pl=true&parts.0={PRODUCT_ID}&location={ZIP_CODE}"
    try:
        data = requests.get(url).json()
    except:
        return "Error fetching API"
    
    stores = []
    for store in data.get("body", {}).get("stores", []):
        for model in store.get("partsAvailability", {}).values():
            if model.get("pickupDisplay") == "available":
                stores.append(store["storeName"])
                break
    if stores:
        subject = f"iPhone Available in {len(stores)} Store(s)!"
        body = f"Good news! Available at these locations near {ZIP_CODE}:\n\n" + "\n".join(stores)
        message = f"Subject: {subject}\n\n{body}"
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(EMAIL_FROM, EMAIL_PASSWORD)
                server.sendmail(EMAIL_FROM, EMAIL_TO, message)
        except:
            return "Error sending email"
        return f"Success! Stores: {', '.join(stores)}"
    return "No stores available"

@app.route("/")
def index():
    result = check_availability_and_notify()
    return result

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)