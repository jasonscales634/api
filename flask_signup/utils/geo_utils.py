import requests
from flask import request

def get_client_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]

def get_country_by_ip(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}")
        if res.status_code == 200:
            return res.json()  # ✅ Dictionary return করবে
    except:
        pass
    return {
        "country": "Unknown",
        "city": "Unknown"
    }