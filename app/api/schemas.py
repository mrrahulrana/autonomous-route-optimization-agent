from pydantic import BaseModel, Field
from typing import List, Optional

class HealthResponse(BaseModel):
    status: str

class Vehicle(BaseModel):
    id: str
    depot_id: int

class Order(BaseModel):
    id: str
    location_id: int
    distance_km: float
    time_of_day: int = Field(ge=0, le=23)
    day_of_week: int = Field(ge=0, le=6)
    traffic_level: int = Field(default=1, ge=0, le=2)

class OptimizeRequest(BaseModel):
    vehicles: List[Vehicle]
    orders: List[Order]
    constraints: Optional[str] = None  # reserved for future LLM use

class RouteSegment(BaseModel):
    vehicle_id: str
    order_id: str
    origin: int
    destination: int
    distance_km: float
    time_of_day: int
    day_of_week: int
    traffic_level: int

class OptimizeResponse(BaseModel):
    routes: dict
    total_eta_min: float
    reasoning: str