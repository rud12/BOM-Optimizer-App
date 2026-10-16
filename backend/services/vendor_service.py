from concurrent.futures import ThreadPoolExecutor, as_completed

from fastapi import HTTPException

from models import Vendor
from services.vendor_clients.digikey import digikey_suggestions, fetch_digikey
from services.vendor_clients.lcsc import fetch_lcsc, lcsc_suggestions
from services.vendor_clients.robu import fetch_robu, robu_suggestions
from services.vendor_clients.mouser import fetch_mouser, mouser_suggestions


VENDOR_FETCHERS = {
    "digikey": fetch_digikey,
    "lcsc": fetch_lcsc,
    "robu": fetch_robu,
    "mouser": fetch_mouser,
}

VENDOR_SUGGESTIONS = {
    "digikey": digikey_suggestions,
    "lcsc": lcsc_suggestions,
    "robu": robu_suggestions,
    "mouser": mouser_suggestions,
}

def list_active_vendors(db):
    return db.query(Vendor).filter(Vendor.is_active == True).order_by(Vendor.name).all()


def get_vendor(db, vendor_name):
    vendor = db.query(Vendor).filter(Vendor.name == vendor_name.lower(), Vendor.is_active == True).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


def get_vendor_products(db, vendor_name, search):
    vendor = get_vendor(db, vendor_name)
    if vendor.name not in VENDOR_FETCHERS:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return VENDOR_FETCHERS[vendor.name](search)


def get_vendor_suggestions(db, vendor_name, query):
    vendor = get_vendor(db, vendor_name)
    if vendor.name not in VENDOR_SUGGESTIONS:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return list(dict.fromkeys(VENDOR_SUGGESTIONS[vendor.name](query)))


def search_all_products(keyword):
    results = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(fetcher, keyword) for fetcher in VENDOR_FETCHERS.values()]
        for future in as_completed(futures):
            try:
                results.extend(future.result())
            except Exception:
                pass
    return sorted(results, key=lambda item: item["moq"][0]["UnitPrice"])


def vendor_id_from_product(db, product):
    vendor = get_vendor(db, product["vendor"])
    return vendor.id if vendor else None
