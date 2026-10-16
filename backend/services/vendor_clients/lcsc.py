from bs4 import BeautifulSoup
from urllib.parse import quote

from services.vendor_clients.common import product_result
from utils.request import curl_get,curl_post
from core.config import DOLLAR_EXCHANGE_RATE


def fetch_lcsc(keyword):
    try:
        response = curl_post(
            "https://wmsc.lcsc.com/ftps/wm/search/v3/global",
            {
                "keyword": keyword,
                "secondKeyword": "",
                "brandIdList": [],
                "catalogIdList": [],
                "isStock": False,
                "isAsianBrand": False,
                "isDeals": False,
                "isEnvironment": False
            },
            headers={
                "origin": "https://www.lcsc.com",
                "referer": "https://www.lcsc.com/"
            }
        )

        if response:
            response = response.json()
            
            result = response["result"]
            scene = result["scene"]

            catalog_id = result["topResults"][0]["catalogId"]

            product_url = f"https://www.lcsc.com/category/{catalog_id}.html?scene={quote(scene)}&globalKeyword={quote(keyword)}&s_z=h_q_{quote(keyword)}"

            product_response = curl_get(product_url)

            if product_response:
                soup = BeautifulSoup(product_response.text,"html.parser")

                items =soup.find_all("tbody")

                if(len(items)>1):
                    product = items[0]

                    row = product.select_one('tr[id^="productId"]')
                    
                    # Product name
                    name = row.find_all("td")[1].get_text().strip().split(" ")[0]

                    # Manufacturer
                    manufacturer = row.find_all("td")[2].find("span").get_text(strip=True)

                    # Availability
                    availability = row.find_all("td")[3].get_text().replace(",", "").split(" ")[0]

                    # Pricing
                    prices = []
                    for tr in row.select("table tr"):
                        tds = tr.select("td")
                        if len(tds) >= 2:
                            prices.append({
                                "BreakQuantity": int(tds[0].get_text(strip=True).replace("+", "").replace(",", "")),
                                "UnitPrice": float(tds[1].get_text(strip=True).replace("$", "")) * DOLLAR_EXCHANGE_RATE
                            })

                    return [
                        product_result(
                            "lcsc",
                            "LCSC",
                            name,
                            manufacturer,
                            prices,
                            availability,
                            product_url
                        )
                    ]
            else:
                print("1")
                return []
        else:
            return []
    except Exception as e:
        print(e)
        return []

def lcsc_suggestions(keyword):
    response = curl_get(
        "https://wmsc.lcsc.com/ftps/wm/search/v2/pre",
        {
            "origin": "https://www.lcsc.com",
            "referer": "https://www.lcsc.com/",
        },
        params={"keyword": keyword},
    )
    
    if response:
        response = response.json()
        values = [
            item["value"]
            for group in (response.get("result") or [])
            for item in (group.get("resultList") or [])
        ]
        return values
    else:
        return []
