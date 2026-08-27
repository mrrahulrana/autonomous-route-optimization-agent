from dataclasses import dataclass
from typing import Optional


@dataclass
class Vehicle:
    id: str
    latitude: float
    longitude: float
    capacity: float = 0.0
    available: bool = True


@dataclass
class DeliveryRequest:
    id: str
    latitude: float
    longitude: float
    demand: float = 0.0
    priority: int = 1
    time_window_start: Optional[str] = None
    time_window_end: Optional[str] = None