import requests

from core.config import DIGIKEY_CLIENT_ID, DIGIKEY_CLIENT_SECRET
from services.vendor_clients.common import product_result
from utils.request import curl_post,curl_get

def get_digikey_token():
    if not DIGIKEY_CLIENT_ID or not DIGIKEY_CLIENT_SECRET:
        return None
    try:
        response = requests.post(
            "https://api.digikey.com/v1/oauth2/token",
            data={
                "client_id": DIGIKEY_CLIENT_ID,
                "client_secret": DIGIKEY_CLIENT_SECRET,
                "grant_type": "client_credentials",
            },
            timeout=10,
        )
        return response.json().get("access_token")
    except Exception:
        return None


def fetch_digikey(keyword):
    token = get_digikey_token()
    if not token:
        return []
    
    response = curl_post(
        "https://api.digikey.com/products/v4/search/keyword",
        {"Keywords": keyword, "Limit": 1},
        {
            "Authorization": f"Bearer {token}",
            "X-DIGIKEY-Client-Id": DIGIKEY_CLIENT_ID,
            "Content-Type": "application/json",
            "X-DIGIKEY-Locale-Site": "IN",
            "X-DIGIKEY-Locale-Language": "en",
            "X-DIGIKEY-Locale-Currency": "INR",
            "X-DIGIKEY-Locale-ShipToCountry": "IN",
        }
    )

    if not response:
        return []

    products = response.json().get("Products", [])
    if not products:
        return []
    product = products[0]

    pricing = product["ProductVariations"][1]["StandardPricing"]

    prices = []
    for p in pricing:
        prices.append(
            {
                "BreakQuantity":p["BreakQuantity"],
                "UnitPrice":p["UnitPrice"]
            }
        )
    
    return [
        product_result(
            "digikey",
            "DigiKey",
            product.get("ManufacturerProductNumber", keyword),
            product.get("Manufacturer", {}).get("Name", ""),
            prices,
            product.get("QuantityAvailable", ""),
            product.get("ProductUrl", "")
        )
    ]


def digikey_suggestions(keyword):
    response = curl_get(
        "https://www.digikey.in/suggestions/v3/search",
        {
            "referer": "https://www.digikey.in/",
            "x-currency": "INR",
            "site": "IN",
            "lang": "en",
        },
        params={"keywordPrefix": keyword, "maxSuggestions": 6}
    )

    if not response:
        return []

    return [item["manufacturerProductNumber"] for item in response.json().get("suggestedProductNumbers", [])]
