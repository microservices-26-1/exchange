from fastapi import FastAPI
from exchangeRouter import router

app = FastAPI(title="Exchange Service")

app.include_router(router)

@app.get("/health-check")
def health_check():
    return {"status": "ok"}