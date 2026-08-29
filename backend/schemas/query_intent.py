from dataclasses import dataclass, field
from typing import Optional


@dataclass
class QueryIntent:
    category: Optional[str] = None

    colours: list[str] = field(default_factory=list)

    min_price: Optional[float] = None
    max_price: Optional[float] = None

    gender: Optional[str] = None
    brand: Optional[str] = None
    material: Optional[str] = None
    fit: Optional[str] = None
    pattern: Optional[str] = None
    sleeve: Optional[str] = None
    occasion: Optional[str] = None
    season: Optional[str] = None

    styles: list[str] = field(default_factory=list)

    hard_constraints: list[str] = field(default_factory=list)
    soft_preferences: list[str] = field(default_factory=list)