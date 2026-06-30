"""
Main API application - FastAPI setup
"""
from fastapi import FastAPI
from src.api.routes import holdings, funds, stocks

app = FastAPI(title="MF Holdings Tracker", version="0.1.0")

# Include routers
app.include_router(holdings.router, prefix="/api/holdings", tags=["holdings"])
app.include_router(funds.router, prefix="/api/funds", tags=["funds"])
app.include_router(stocks.router, prefix="/api/stocks", tags=["stocks"])


@app.get("/")
def read_root():
    """Health check endpoint"""
    return {"message": "MF Holdings Tracker API is running"}
