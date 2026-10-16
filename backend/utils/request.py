from curl_cffi import requests

def curl_get(url, headers=None, **kwargs):
    try:
        response = requests.get(
            url,
            headers={
                "accept": "application/json, text/plain, */*",
                "user-agent": (
                    "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/148.0.0.0 Mobile Safari/537.36"
                ),
                **(headers or {})
            },
            impersonate="chrome136",
            **kwargs)
        return response
    except Exception as err:
        return None
    
def curl_post(url,payload, headers=None, **kwargs):
    try:
        response = requests.post(
            url,
            json=payload,
            headers={
                "accept": "application/json, text/plain, */*",
                "content-type": "application/json;charset=UTF-8",
                "user-agent": (
                    "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/148.0.0.0 Mobile Safari/537.36"
                ),
                **(headers or {})
            },
            impersonate="chrome136",
            **kwargs)
        return response
    except Exception as err:
        return None