from fastapi import APIRouter, HTTPException, Request
from datetime import datetime
import requests
import os

router = APIRouter()

API_KEY = os.getenv("EXCHANGE_API_KEY")

@router.get("/exchange/{from_currency}/{to_currency}")
def exchange(request: Request, from_currency: str, to_currency: str):
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    response = requests.get(
        f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{from_currency}"
    )

    if not response.ok:
        raise HTTPException(status_code=404, detail="Exchange rate not found")

    data = response.json()

    if data.get("result") != "success":
        raise HTTPException(status_code=404, detail="Exchange rate not found")

    rate = data["conversion_rates"].get(to_currency)
    
    if rate is None:
        raise HTTPException(status_code=404, detail=f"Currency {to_currency} not found")

    return {
        "sell": float(rate),
        "buy": float(rate),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "id-account": request.headers.get("id-account")
    }