from fastapi import APIRouter, HTTPException, Request
from datetime import datetime
import requests

router = APIRouter()

_cache = {}
_CACHE_TTL_SECONDS = 60

@router.get("/exchange/{from_currency}/{to_currency}")
def exchange(request: Request, from_currency: str, to_currency: str):
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    key = from_currency + to_currency

    if key in _cache:
        cached_at, cached_data = _cache[key]
        if (datetime.now() - cached_at).seconds < _CACHE_TTL_SECONDS:
            return cached_data

    response = requests.get(
        f"https://economia.awesomeapi.com.br/json/last/{from_currency}-{to_currency}"
    )

    if not response.ok:
        raise HTTPException(status_code=404, detail="Exchange rate not found")

    data = response.json()
    if key not in data:
        raise HTTPException(status_code=404, detail="Exchange rate not found")

    rate = data[key]
    result = {
        "sell": float(rate["ask"]),
        "buy": float(rate["bid"]),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "id-account": request.headers.get("id-account")
    }

    _cache[key] = (datetime.now(), result)
    return result