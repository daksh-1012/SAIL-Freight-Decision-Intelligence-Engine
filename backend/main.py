from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from decision_engine import run_decision
from forecasting.xgboost_forecast import forecast_future
from scenario_engine import build_scenarios


app = FastAPI(
    title="SAIL Freight Decision Intelligence Engine",
    description="Decision support API for vessel chartering and bulk cargo procurement",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


class ScenarioRequest(BaseModel):
    cargo_quantity: int
    current_rate: float
    forecast_7: float
    forecast_14: float
    distance_nm: float
    vessel_speed: float
    fuel_price: float
    fuel_consumption: float
    port_cost: float
    waiting_days: float
    demurrage_per_day: float
    probability_7: float
    probability_14: float

    risk_7: float = 0
    risk_14: float = 0

    freight_change_pct: float = Field(default=10, ge=-30, le=30)
    fuel_change_pct: float = Field(default=15, ge=-30, le=30)
    waiting_days_change: float = Field(default=2, ge=-5, le=10)


@app.get("/")
def root():
    return {
        "message": "SAIL Freight Decision Engine API",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/api/forecast")
def get_forecast(
    vessel_class: str = "Panamax",
    days: int = 30
):
    forecast = forecast_future(
        vessel_class=vessel_class,
        days=days
    )

    return {
        "vessel_class": vessel_class,
        "days": days,
        "forecast": forecast
    }


@app.get("/api/decision")
def get_decision(
    cargo_quantity: int = 50000,
    origin: str = "Australia",
    destination: str = "Dhamra"
):
    return run_decision(
        cargo_quantity=cargo_quantity,
        origin=origin,
        destination=destination
    )


@app.post("/api/scenario")
def run_scenario(request: ScenarioRequest):
    return build_scenarios(**request.model_dump())