import smtplib
import requests
import time
import json

# ============================
# SETTINGS (edit these!)
# ============================
ZIP_CODE = "22204"   # Replace with your ZIP code
# ZIP_CODE = "89511"   # SEATTLE
PRODUCT_ID = "MFXH4LL/A"  # Replace with the actual Apple SKU for your iPhone model
CHECK_INTERVAL = 1800  # seconds (30 min)

# Email settings
EMAIL_FROM = "zoljargal.byam@gmail.com"
EMAIL_TO = "zoljargal.shift@gmail.com"
EMAIL_PASSWORD = "hnha ozed otrq wvtp"  # Gmail App Password

def check_availability():
    url = f"https://www.apple.com/shop/retail/pickup-message?pl=true&parts.0={PRODUCT_ID}&location={ZIP_CODE}"
    response = requests.get(url)

    try:
        data = response.json()
    except json.JSONDecodeError:
        print("⚠️ Response not JSON. Got:", response.text[:300])
        return []

    if "body" not in data or "stores" not in data["body"]:
        error = data.get("body", {}).get("errorMessage", "Unknown error")
        print(f"⚠️ API returned error: {error}")
        return []

    available_stores = []
    stores = data["body"]["stores"]
    for store in stores:
        for model in store.get("partsAvailability", {}).values():
            if model.get("pickupDisplay") == "available":
                available_stores.append(store["storeName"])
                break  # don’t repeat same store multiple times
    return available_stores


def send_email(stores):
    subject = f"iPhone Available in {len(stores)} Store(s)!"
    body = "Good news! iPhone is available at these locations near {zip}:\n\n".format(zip=ZIP_CODE)
    body += "\n".join(stores)
    message = f"Subject: {subject}\n\n{body}"

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, message)


print(f"🔍 Monitoring iPhone ({PRODUCT_ID}) availability near {ZIP_CODE}...")
while True:
    available_stores = check_availability()
    if available_stores:
        print("✅ Found in these stores:")
        for s in available_stores:
            print("   -", s)
        send_email(available_stores)
        break
    else:
        print("❌ Not available yet. Checking again later...")
    time.sleep(CHECK_INTERVAL)