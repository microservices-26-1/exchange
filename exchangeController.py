import httpx

class ExchangeController:
    def __init__(self):
        self.base_url = "http://exchange:8080"
    
    def get_currency(self, curr: str):
        with httpx.Client() as client:
            return client.get(f"{self.base_url}/{curr}").json()
