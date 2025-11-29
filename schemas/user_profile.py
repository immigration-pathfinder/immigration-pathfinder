# schemas/user_profile.py

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
    # e.g. "bachelor", "master"
    degree_level: str
    # رشته می‌تونه خالی باشه، پس Optional
    field_of_study: Optional[str] = None


class WorkExperience(BaseModel):
    occupation: str
    # float چون ممکنه 2.5 سال تجربه داشته باشیم
    years_of_experience: float = Field(..., ge=0)


class LanguageProficiency(BaseModel):
    """
    Compatible with:
    - dict پروفایل که از ProfileAgent می‌آید (english_level, english_score)
    - ExplainAgent و Orchestrator
    """

    # IELTS score (اختیاری – اگر نبود 0)
    ielts_score: float = Field(0.0, ge=0.0, le=9.0)

    # CEFR A1–C2
    cefr_level: str = "A1"

    # زبان‌های اضافی (اختیاری)
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

    immigration_goal: str                    # "Study" / "Work" / "PR"
    preferred_countries: List[str] = []      # لیست کشورهای مورد علاقه
    goals: List[str] = []                    # اهداف فرعی
    target_countries: List[str] = []         # همون target_countries که تو Orchestrator استفاده می‌کنی
