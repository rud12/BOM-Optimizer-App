from utils.request import curl_post
from services.vendor_clients.common import product_result


def fetch_robu(keyword):
    try:
        response = curl_post(
            "https://robu.in/api/proxy/graphql/",
            {
                "operationName": "ProductSearch",
                "variables": {"search": keyword},
                "query": (
                    "query ProductSearch($search:String!)"
                    "{productSearch(search:$search)"
                    "{data{products{name slug sku price in_stock}}}}"
                ),
            },
            {
                "origin": "https://robu.in",
                "referer": "https://robu.in/",
            }
        )

        if not response:
            return []

        print(response.text)
        products = response.json()["data"]["productSearch"]["data"]["products"]

        if not products:
            return []

        product = products[0]

        slug = product.get("slug", "")

        if not slug:
            return []

        res = curl_post(
            "https://robu.in/api/proxy/graphql/",
            {
                "operationName": "ProductDetails",
                "variables": {
                    "slug": slug
                },
                "query": """
                query ProductDetails($slug: String!) {
                productdetails(slug: $slug) {
                    data {
                    name
                    short_description
                    available_quantity
                    product_brand {
                        name
                        slug
                    }
                    price {
                        final
                        regular
                    }
                    moq_prices {
                        range_from
                        range_to
                        price
                    }
                    }
                }
                }
                """
            })
        
        if not res:
            return []
        
        resp = res.json()
            
        name = resp["data"]["productdetails"]["data"]["name"]
        brand = resp["data"]["productdetails"]["data"]["product_brand"][0].get("name", None)
        stock = resp["data"]["productdetails"]["data"].get("available_quantity", 0)
        url = f"https://robu.in/product/{slug}/"

        prices = []
        moq_prices = resp["data"]["productdetails"]["data"].get("moq_prices", [])
        if not moq_prices:
            prices.append({
                "BreakQuantity": 1,
                "UnitPrice": resp["data"]["productdetails"]["data"]["price"]["final"],
            })
        else:
            for moq in moq_prices:
                prices.append({
                    "BreakQuantity": moq["range_from"],
                    "UnitPrice": moq["price"],
                })

        return [
            product_result(
                "robu",
                "Robu",
                name,
                brand,
                prices,
                stock,
                url,
            )
        ]
    except Exception as e:
        return []


def robu_suggestions(keyword):
    response = curl_post(
        "https://robu.in/api/proxy/graphql/",
        {
            "operationName": "ProductSearch",
            "variables": {"search": keyword},
            "query": (
                "query ProductSearch($search:String!)"
                "{productSearch(search:$search){data{products{name sku}}}}"
            ),
        },
        {
            "origin": "https://robu.in",
            "referer": "https://robu.in/",
        }
    )
    if not response:
        return []
    
    products = response.json()["data"]["productSearch"]["data"]["products"]
    return [product["name"] for product in products]
