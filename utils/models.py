from pydantic import BaseModel
from typing import List, Optional

# NOTE: every Optional[...] field below is given an explicit `= None` (or
# `= []` via default_factory-equivalent literal for lists) default. In
# Pydantic v2, `Optional[str]` alone does NOT make a field optional to omit -
# it only allows None as a valid *value* for a field that must still be
# supplied. Without an explicit default, callers like utils/parsers.py that
# build partial dicts (omitting keys that had no regex match) would trigger
# "Field required" validation errors even though the field is logically
# optional. Explicit defaults fix that.

class Review(BaseModel):
    rating: Optional[float] = None
    highlights: List[str] = []

class Booking(BaseModel):
    confirmation: Optional[str] = None
    cancellation_policy: Optional[str] = None
    payment_options: List[str] = []
    reviews: Review = Review()
    status: Optional[str] = None

class Hotel(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    room_types: List[str] = []
    amenities: List[str] = []
    price_range: Optional[str] = None
    reviews: Review = Review()
    fit: Optional[str] = None

class Restaurant(BaseModel):
    name: Optional[str] = None
    cuisine: Optional[str] = None
    dietary_options: List[str] = []
    seating: Optional[str] = None
    price_range: Optional[str] = None
    reviews: Review = Review()
    fit: Optional[str] = None

class Transport(BaseModel):
    mode: Optional[str] = None
    duration: Optional[str] = None
    price_range: Optional[str] = None
    availability: Optional[str] = None
    reviews: Review = Review()
    fit: Optional[str] = None

class Alert(BaseModel):
    type: str = "General"
    message: str
    severity: Optional[str] = None  # Low, Medium, High

class Event(BaseModel):
    name: str
    date: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    price_range: Optional[str] = None
    reviews: Optional[List[str]] = None

class Location(BaseModel):
    name: str
    type: Optional[str] = None  # Landmark, Museum, Park
    opening_hours: Optional[str] = None
    price_range: Optional[str] = None
    reviews: Optional[List[str]] = None

class News(BaseModel):
    headline: str
    source: Optional[str] = None
    date: Optional[str] = None
    summary: Optional[str] = None
