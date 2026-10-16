def product_result(vendor, display_name, name, manufacturer, moq, stock, product_url):
    for i in moq:
        i["BreakQuantity"] = int(i["BreakQuantity"])
        i["UnitPrice"] = float(i["UnitPrice"])

    return {
        "vendor": vendor,
        "vendor_display_name": display_name,
        "component_name": name,
        "manufacturer": manufacturer,
        "moq": moq,
        "stock": str(stock or ""),
        "product_url": product_url or "",
    }
# def product_result(vendor, display_name, name, manufacturer, unit_price, stock, product_url, moq=None):
#     if moq:
#         for i in moq:
#             i["BreakQuantity"] = int(i["BreakQuantity"])
#             i["UnitPrice"] = float(i["UnitPrice"])

#     return {
#         "vendor": vendor,
#         "vendor_display_name": display_name,
#         "component_name": name,
#         "manufacturer": manufacturer,
#         "unit_price": float(unit_price),
#         "stock": str(stock or ""),
#         "moq": moq,
#         "product_url": product_url or "",
#     }
