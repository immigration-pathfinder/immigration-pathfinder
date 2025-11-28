from pydantic import BaseModel, Field
from typing import Optional, List

class PersonalInfo(BaseModel):
    first_name: str
    last_name: str
    age: int = Field(..., ge=0, le=100)
    nationality: str
    current_residence: str
    marital_status: str

class Education(BaseModel):
    degree_level: str
    field_of_study: str

class WorkExperience(BaseModel):
    occupation: str
    years_of_experience: int = Field(..., ge=0)

class LanguageProficiency(BaseModel):
    ielts_score: float = Field(..., ge=0.0, le=9.0)
    german_level: Optional[str] = None
    french_level: Optional[str] = None

class FinancialInfo(BaseModel):
    liquid_assets_usd: float = Field(..., ge=0.0)

class UserProfile(BaseModel):
    personal_info: PersonalInfo
    education: Education
    work_experience: WorkExperience
    language_proficiency: LanguageProficiency
    financial_info: FinancialInfo
    immigration_goal: str
    preferred_countries: List[str]