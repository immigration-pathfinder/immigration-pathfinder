from pydantic import BaseModel, Field
from typing import List, Optional

class RankedCountry(BaseModel):
    country: str
    pathway: str
    score: float
    reason: Optional[str] = None

class CountryRanking(BaseModel):
    ranked_countries: List[RankedCountry]