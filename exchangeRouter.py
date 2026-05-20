from datetime import datetime
from fastapi import APIRouter, Cookie, HTTPException, Request
import requests

router = APIRouter()

@router.get("/exchanges/{from_currency}/{to_currency}")
def exchange(
    request: Request,
    from_currency: str,
    to_currency: str,
):

    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    response = requests.get(
        f"https://economia.awesomeapi.com.br/json/last/{from_currency}-{to_currency}"
    )

    if not response.ok:
        raise HTTPException(status_code=404, detail="Exchange rate not found")
    
    data = response.json()
    key = from_currency + to_currency
    
    if key not in data:
        raise HTTPException(status_code=404, detail="Exchange rate not found")

    rate = data[key]
    
    return {
        "sell": float(rate["ask"]),  
        "buy": float(rate["bid"]),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "id-account": request.headers.get("id-account")
    }