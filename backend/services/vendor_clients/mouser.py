from bs4 import BeautifulSoup  # kept only to match your style; not needed for API parsing
import re

from core.config import MOUSER_API_KEY
from services.vendor_clients.common import product_result
from utils.request import curl_post



def fetch_mouser(keyword):
    response = curl_post(
        f"https://api.mouser.com/api/v1/search/keyword?apiKey={MOUSER_API_KEY}",
        {
            "SearchByKeywordRequest": {
                "keyword": keyword,
                "records": 10,
                "startingRecord": 0,
                "searchOptions": "None",
                "searchWithYourSignUpLanguage": "false"
            }
        },
        {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "origin": "https://www.mouser.in",
            "referer": "https://www.mouser.in/",
            "x-requested-with": "XMLHttpRequest",
        }
    )

    if not response:
        return []

    response = response.json()
    part = (((response or {}).get("SearchResults") or {}).get("Parts") or [])[0]

    results = []

    name = part.get("ManufacturerPartNumber") or part.get("MouserPartNumber") or ""
    manufacturer = part.get("Manufacturer") or ""
    stock = int(part.get("Availability","0").split()[0])
    product_url = part.get("ProductDetailUrl") or ""

    price_breaks = part.get("PriceBreaks") or []

    prices = []
    if price_breaks:
        for p in price_breaks:
            prices.append(
                {
                    "BreakQuantity": p["Quantity"],
                    "UnitPrice": float(p["Price"].replace("₹", "").replace(",", "").strip())
                }
            )

    return [ product_result(
        "Mouser",
        "mouser",
        name,
        manufacturer,
        prices,
        stock,
        product_url,
    )]


def mouser_suggestions(keyword):
    return [keyword]