from typing import Any, Dict, List, Optional
import json
import re
from tools.logger import Logger


# -------------------------------------------------------
#  Profile schema fields
# -------------------------------------------------------
PROFILE_FIELDS: List[str] = [
    "age",
    "citizenship",
    "marital_status",
    "education_level",
    "field_of_study",
    "english_score",
    "english_level",
    "funds_usd",
    "work_experience_years",
    "goal",              # Work / Study / PR
    "target_countries",
]

REQUIRED_FIELDS: List[str] = [
    "age",
    "education_level",
    "goal",
]


# -------------------------------------------------------
#  ProfileAgent Class
# -------------------------------------------------------
class ProfileAgent:
    """
    Extracts a structured user profile from raw text.

    Supports two modes:
    - Rule-based mock extractor (default)
    - Gemini-based extraction (later, in Kaggle environment)
    """

    def __init__(self, logger: Optional[Logger] = None, use_gemini: bool = False) -> None:
        self.logger = logger or Logger()
        self.use_gemini = use_gemini

    # ---------------------------------------------------
    #  Public entry point
    # ---------------------------------------------------
    def run(self, raw_text: str) -> Dict[str, Any]:
        """Main profile extraction pipeline."""

        if self.logger:
            self.logger.log_agent_call(
                agent_name="ProfileAgent",
                session_id=None,
                input_summary=raw_text[:200],
            )

        try:
            # Choose extraction method
            if self.use_gemini:
                profile = self._extract_with_gemini(raw_text)
            else:
                profile = self._extract_mock(raw_text)

        except Exception as e:
            if self.logger:
                self.logger.log_exception(e, context="ProfileAgent.run")
            profile = self._empty_profile()
            profile["errors"] = ["unexpected_error_in_extraction"]

        # Normalize data
        profile = self._normalize_profile(profile)

        # Validate required fields
        errors = self._validate_profile(profile)
        if errors:
            profile["errors"] = errors

        return profile

    # ---------------------------------------------------
    #  Gemini Extractor (placeholder)
    # ---------------------------------------------------
    def _extract_with_gemini(self, raw_text: str) -> Dict[str, Any]:
        """
        LLM-based extractor using Gemini.
        (In Kaggle, this will call gemini_model.generate_content)

        Currently falls back to rule-based mock.
        """

        if self.logger:
            self.logger.log_tool_call(
                tool_name="GeminiNLP",
                params={"component": "ProfileAgent", "mode": "extract_user_profile"},
            )

        # TODO: Add real Gemini call inside Kaggle environment
        return self._extract_mock(raw_text)

    # ---------------------------------------------------
    #  Mock Extractor (Rule-based)
    # ---------------------------------------------------
    def _extract_mock(self, raw_text: str) -> Dict[str, Any]:
        """Simple rule-based extractor for local dev."""

        text_low = raw_text.lower()
        profile = self._empty_profile()

        # --- Age ---
        age_match = re.search(r"(\d{2})\s+years\s+old", text_low)
        if age_match:
            try:
                profile["age"] = int(age_match.group(1))
            except ValueError:
                pass

        # --- Citizenship ---
        if "iran" in text_low:
            profile["citizenship"] = "Iran"

        # --- Goal ---
        if " work " in f" {text_low} " or "job" in text_low:
            profile["goal"] = "Work"
        elif " study " in f" {text_low} " or "university" in text_low:
            profile["goal"] = "Study"
        elif " pr " in f" {text_low} " or "permanent residency" in text_low:
            profile["goal"] = "PR"

        # --- Region / Country Preference ---
        if "europe" in text_low:
            profile["target_countries"] = ["Germany", "Netherlands"]

        return profile

    # ---------------------------------------------------
    #  JSON Parser for Gemini Output
    # ---------------------------------------------------
    def _parse_gemini_output(self, text: str) -> Dict[str, Any]:
        """
        Clean Gemini output and parse JSON safely.
        Handles code fences and messy formatting.
        """

        raw = text.strip()

        # Remove Markdown fences
        if raw.startswith("```"):
            raw = raw.strip("`")

        # Extract JSON substring
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1:
            raw_json = raw[start : end + 1]
        else:
            raw_json = raw

        try:
            data = json.loads(raw_json)
        except Exception as e:
            if self.logger:
                self.logger.log_exception(e, context="ProfileAgent._parse_gemini_output")
            data = self._empty_profile()
            data["errors"] = ["gemini_json_parse_failed"]

        return data

    # ---------------------------------------------------
    #  Empty Profile Template
    # ---------------------------------------------------
    def _empty_profile(self) -> Dict[str, Any]:
        """Return an empty profile with all required keys."""
        profile = {}
        for field in PROFILE_FIELDS:
            profile[field] = [] if field == "target_countries" else None
        return profile

    # ---------------------------------------------------
    #  Validation
    # ---------------------------------------------------
    def _validate_profile(self, profile: Dict[str, Any]) -> List[str]:
        errors = []

        # Required fields
        for field in REQUIRED_FIELDS:
            if profile.get(field) in (None, "", []):
                errors.append(f"missing_required_field:{field}")

        # Age check
        age = profile.get("age")
        if age is not None:
            try:
                age_int = int(age)
                if age_int <= 0 or age_int > 100:
                    errors.append("invalid_age_range")
            except (ValueError, TypeError):
                errors.append("invalid_age_type")

        return errors

    # ---------------------------------------------------
    #  Normalization
    # ---------------------------------------------------
    def _normalize_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize whitespace, casing, and structure."""

        normalized = {}

        for field in PROFILE_FIELDS:
            value = profile.get(field)

            # Trim strings
            if isinstance(value, str):
                value = value.strip()

            # Capitalization for citizenship
            if field == "citizenship" and isinstance(value, str):
                value = value.title()

            normalized[field] = value

        return normalized


# -------------------------------------------------------
#  Local test runner
# -------------------------------------------------------
if __name__ == "__main__":
    agent = ProfileAgent()
    text = (
        "I'm a 32 years old Iranian, single, with a master's degree in computer science, "
        "IELTS 6.5, 5 years of work experience, around 15000 USD savings, "
        "and I'm looking for work opportunities in Europe."
    )
    output = agent.run(text)
    print(output)
    print(output.keys())
