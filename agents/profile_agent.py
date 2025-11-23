from typing import Any, Dict, List, Optional
import re


USER_PROFILE_FIELDS: List[str] = [
    "age",
    "citizenship",
    "marital_status",
    "education_level",
    "field",
    "ielts",
    "german_level",
    "french_level",
    "funds_usd",
    "work_experience_years",
    "goal",
    "preferred_region",
]


class ProfileAgent:
    """
    ProfileAgent

    Takes a free-form user description and converts it
    into a structured UserProfile dict that matches:

    {
        "age": int,
        "citizenship": str,
        "marital_status": str,
        "education_level": str,
        "field": str,
        "ielts": float,
        "german_level": str,
        "french_level": str,
        "funds_usd": float,
        "work_experience_years": float,
        "goal": str,
        "preferred_region": [str]
    }
    """

    def __init__(self, logger: Optional[Any] = None) -> None:
        self.logger = logger

    def run(self, user_text: str) -> Dict[str, Any]:
        """
        Extract structured UserProfile fields from user free text.
        """

        if self.logger:
            self.logger.log_agent_call(
                agent_name="ProfileAgent",
                session_id=None,
                input_summary=user_text[:200],
            )

        # Base structure for a valid UserProfile
        profile: Dict[str, Any] = {
            "age": None,
            "citizenship": None,
            "marital_status": None,
            "education_level": None,
            "field": None,
            "ielts": None,
            "german_level": None,
            "french_level": None,
            "funds_usd": None,
            "work_experience_years": None,
            "goal": None,
            "preferred_region": []
        }

        text_low = user_text.lower()

        # -------------------------------
        # SIMPLE RULE-BASED EXTRACTION
        # -------------------------------

        # extract age: "32 years old"
        age_match = re.search(r"(\d{2})\s+years\s+old", text_low)
        if age_match:
            try:
                profile["age"] = int(age_match.group(1))
            except ValueError:
                pass

        # citizenship
        if "iran" in text_low:
            profile["citizenship"] = "Iran"

        # goal
        if " work " in f" {text_low} " or "job" in text_low:
            profile["goal"] = "Work"
        elif " study " in f" {text_low} " or "university" in text_low:
            profile["goal"] = "Study"
        elif " pr " in f" {text_low} " or "permanent residency" in text_low:
            profile["goal"] = "PR"

        # region
        regions = []
        if "europe" in text_low:
            regions.append("Europe")
        if "canada" in text_low or "usa" in text_low or "united states" in text_low:
            regions.append("North America")
        if regions:
            profile["preferred_region"] = regions

        # Return normalized profile
        return self._normalize_profile(profile)

    def _normalize_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cleanup + normalization of extracted fields:
        - trim strings
        - proper casing for countries
        - convert regions into normalized list
        """

        normalized: Dict[str, Any] = {}

        for field in USER_PROFILE_FIELDS:
            if field not in profile:
                continue

            value = profile[field]

            # trim string fields
            if isinstance(value, str):
                value = value.strip()

            # normalize country names
            if field == "citizenship" and isinstance(value, str):
                value = value.title()

            # normalize region field
            if field == "preferred_region":
                if isinstance(value, str):
                    value = [value]
                if isinstance(value, list):
                    value = [str(v).strip() for v in value]

            normalized[field] = value

        return normalized
if __name__ == "__main__":
    agent = ProfileAgent()

    text = "I'm a 32 years old Iranian, single, looking for work in Europe. IELTS 6.5, 5 years work experience, 15000 USD savings."

    profile = agent.run(text)
    print(profile)
    print(profile.keys())
