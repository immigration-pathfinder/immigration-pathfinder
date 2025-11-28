import sys
from pathlib import Path
from typing import Any, Dict, Optional, List
import re

# ----------------------------------------------------
# اختیاری: اگر خواستی مستقل هم ران بشه، روت پروژه رو اضافه کن
# ----------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ----------------------------------------------------
# LOGGER (safe import + toggle)
# ----------------------------------------------------
try:
    from tools.logger import Logger, LOGGING_ENABLED as LOGGER_DEFAULT_ENABLED
except Exception:
    Logger = None            # type: ignore
    LOGGER_DEFAULT_ENABLED = False

LOGGER_LOCAL_ENABLED = False        # اینو اگر خواستی لاگ روشن شه کن True
LOGGING_ENABLED = LOGGER_DEFAULT_ENABLED and LOGGER_LOCAL_ENABLED
# ----------------------------------------------------


class ProfileAgent:
    """
    ProfileAgent

    Phase 5.2:
      - Take raw user text
      - Extract a structured migration profile
      - Use simple, transparent, rule-based parsing (no LLM here)
    """

    def __init__(self, logger: Optional["Logger"] = None) -> None:
        # مثل بقیه ایجنت‌ها: اگر logger پاس دادی همون، اگر نه و LOGGING فعال بود Logger() بساز
        if logger is not None:
            self.logger = logger
        elif Logger and LOGGING_ENABLED:
            self.logger = Logger()
        else:
            self.logger = None

    def _extract_age(self, text: str) -> Optional[int]:
        # e.g. "I am 30 years old" or "I'm 30 years old"
        m = re.search(r"\b(?:I am|I'm)\s+(\d{2})\s+years?\s+old\b", text, re.IGNORECASE)
        if m:
            try:
                return int(m.group(1))
            except ValueError:
                return None
        return None

    def _extract_citizenship(self, text: str) -> Optional[str]:
        # e.g. "from Iran", "I am Iranian"
        m = re.search(r"\bfrom\s+([A-Za-z ]+)\b", text, re.IGNORECASE)
        if m:
            return m.group(1).strip()

        m2 = re.search(r"\bI am\s+([A-Za-z]+ian)\b", text, re.IGNORECASE)
        if m2:
            return m2.group(1).strip().capitalize()

        return None

    def _extract_education_level(self, text: str) -> Optional[str]:
        # map phrases to normalized levels
        text_lower = text.lower()
        if "phd" in text_lower or "doctorate" in text_lower:
            return "phd"
        if "master" in text_lower or "m.sc" in text_lower or "msc" in text_lower:
            return "master"
        if "bachelor" in text_lower or "b.sc" in text_lower or "bsc" in text_lower:
            return "bachelor"
        if "diploma" in text_lower:
            return "diploma"
        if "high school" in text_lower:
            return "high_school"
        return None

    def _extract_field_of_study(self, text: str) -> Optional[str]:
        # very simple heuristic
        m = re.search(r"\bdegree in ([A-Za-z ]+)\b", text, re.IGNORECASE)
        if m:
            return m.group(1).strip().lower()

        # fallback: look for "my field of study is ..."
        m2 = re.search(r"field of study is ([A-Za-z ]+)\b", text, re.IGNORECASE)
        if m2:
            return m2.group(1).strip().lower()

        return None

    def _extract_work_experience_years(self, text: str) -> Optional[float]:
        # e.g. "2 years of work experience" or "I have 2 years of experience"
        m = re.search(r"\b(\d+(?:\.\d+)?)\s+years?\s+of\s+(?:work )?experience\b", text, re.IGNORECASE)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                return None

        # e.g. "I have no work experience"
        if re.search(r"\bno work experience\b", text, re.IGNORECASE) or \
           re.search(r"\bdo not have (any )?work experience\b", text, re.IGNORECASE):
            return 0.0

        return None

    def _extract_english_level(self, text: str) -> Optional[str]:
        # Look for CEFR levels A1–C2
        m = re.search(r"\b(A1|A2|B1|B2|C1|C2)\b", text, re.IGNORECASE)
        if m:
            return m.group(1).upper()
        return None

    def _extract_english_score(self, text: str) -> Optional[float]:
        # e.g. "IELTS 6.5", "IELTS score 7"
        m = re.search(r"\bIELTS\s+(\d(?:\.\d)?)\b", text, re.IGNORECASE)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                return None
        return None

    def _extract_funds_usd(self, text: str) -> Optional[float]:
        # e.g. "10000 USD", "10,000 dollars"
        m = re.search(r"\b(\d{3,}(?:,\d{3})*(?:\.\d+)?)\s*(USD|dollars?)\b", text, re.IGNORECASE)
        if m:
            num_str = m.group(1).replace(",", "")
            try:
                return float(num_str)
            except ValueError:
                return None
        return None

    def _extract_goal(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        if ("work visa" in text_lower or "job" in text_lower or
            "work-based" in text_lower or "my goal is work" in text_lower):
            return "Work"
        if ("study visa" in text_lower or "student visa" in text_lower or
            "my goal is study" in text_lower):
            return "Study"
        if "permanent residency" in text_lower or "pr" in text_lower:
            return "PR"
        return None

    def _extract_target_countries(self, text: str) -> List[str]:
        # super simple: look for "Germany", "Netherlands", etc.
        countries: List[str] = []
        candidates = ["Germany", "Netherlands", "Canada", "Australia", "Sweden", "UK"]
        for c in candidates:
            if re.search(r"\b" + re.escape(c) + r"\b", text, re.IGNORECASE):
                countries.append(c)
        return countries

    def run(self, raw_text: str) -> Dict[str, Any]:
        """
        Main entry: extract a structured migration profile from raw_text.
        """

        # Logging
        if self.logger:
            self.logger.log_agent_call(
                agent_name="ProfileAgent",
                session_id=None,
                input_summary=raw_text[:200],
            )

        text = raw_text.strip()

        age = self._extract_age(text)
        citizenship = self._extract_citizenship(text)
        education_level = self._extract_education_level(text)
        field_of_study = self._extract_field_of_study(text)
        work_experience_years = self._extract_work_experience_years(text)
        english_level = self._extract_english_level(text)
        english_score = self._extract_english_score(text)
        funds_usd = self._extract_funds_usd(text)
        goal = self._extract_goal(text)
        target_countries = self._extract_target_countries(text)

        errors: List[str] = []

        # Minimal validation (Phase 5.2)
        if age is None:
            errors.append("missing_required_field:age")
        if education_level is None:
            errors.append("missing_required_field:education_level")

        profile: Dict[str, Any] = {
            "age": age,
            "citizenship": citizenship,
            "marital_status": None,  # not extracted in this phase
            "education_level": education_level,
            "field_of_study": field_of_study,
            "english_score": english_score,
            "english_level": english_level,
            "funds_usd": funds_usd,
            "work_experience_years": work_experience_years,
            "goal": goal,
            "target_countries": target_countries,
            "errors": errors,
        }

        return profile
