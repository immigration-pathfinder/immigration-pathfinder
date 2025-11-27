# agents/match_agent.py

import sys
from pathlib import Path

# Add project root so we can import tools, rules, agents, ...
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from typing import List, Dict, Any, Tuple, Optional
from tools.logger import Logger


DEGREE_ORDER = {
    "high school": 0,
    "high_school": 0,
    "diploma": 1,
    "bachelor": 2,
    "master": 3,
    "phd": 4,
}


class MatchAgent:
    """Compare UserProfile against country/pathway rules."""

    # Scoring thresholds
    SCORE_OK = 0.75
    SCORE_BORDERLINE = 0.4
    MAX_PENALTIES = 5
    LARGE_FUNDS_GAP = 5000

    def __init__(self, rules: List[Dict[str, Any]], logger: Optional[Logger] = None) -> None:
        """
        Args:
            rules: List of rule dicts from country_rules.json
        """
        if not rules:
            raise ValueError("Rules list cannot be empty")
        self.rules = rules
        self.logger = logger or Logger()

    def _normalize_degree(self, degree: str) -> str:
        """Normalize degree name for comparison."""
        if not degree:
            return ""
        return degree.lower().strip().replace(" ", "_")

    def _score_single_rule(
        self,
        profile: Dict[str, Any],
        rule: Dict[str, Any],
    ) -> Tuple[str, float, Dict[str, Any]]:
        """
        Compare profile against one rule.

        Returns:
            (status, score, gaps)
        """
        missing: List[str] = []
        risks: List[str] = []
        penalties = 0

        # Age check
        age = profile.get("age")
        min_age = rule.get("minimum_age")
        max_age = rule.get("maximum_age") or rule.get("age_max")

        if age is not None:
            if min_age and age < min_age:
                missing.append(f"Age {age} below minimum {min_age}")
                penalties += 1
            if max_age and age > max_age:
                missing.append(f"Age {age} above maximum {max_age}")
                penalties += 1

        # Degree check
        profile_degree = self._normalize_degree(profile.get("education_level", ""))
        required_degree = self._normalize_degree(
            rule.get("min_degree") or rule.get("minimum_degree", "")
        )

        if profile_degree and required_degree:
            profile_rank = DEGREE_ORDER.get(profile_degree, -1)
            required_rank = DEGREE_ORDER.get(required_degree, -1)

            if profile_rank < 0:
                missing.append(f"Unknown degree level: {profile_degree}")
                penalties += 1
            elif profile_rank < required_rank:
                missing.append(
                    f"Degree '{profile_degree}' below required '{required_degree}'"
                )
                penalties += 1

        # IELTS check
        profile_ielts = profile.get("ielts")
        required_ielts = rule.get("min_ielts") or rule.get("minimum_ielts")

        if required_ielts is not None:
            if profile_ielts is None:
                missing.append("IELTS score not provided")
                penalties += 1
            elif profile_ielts < required_ielts:
                missing.append(
                    f"IELTS {profile_ielts} below required {required_ielts}"
                )
                penalties += 1

        # Funds check
        funds = profile.get("funds_usd")
        required_funds = (
            rule.get("min_funds_usd")
            or rule.get("minimum_funds_usd")
            or rule.get("minimum_income_usd")
        )

        if required_funds is not None:
            if funds is None:
                missing.append("Funds information not provided")
                penalties += 1
            elif funds < required_funds:
                gap = required_funds - funds
                missing.append(
                    f"Insufficient funds (need ${required_funds}, have ${funds})"
                )
                penalties += 1

                if gap > self.LARGE_FUNDS_GAP:
                    risks.append(
                        f"Large funds gap (${gap}) may increase visa refusal risk"
                    )

        # Work experience check
        years = profile.get("work_experience_years")
        required_years = (
            rule.get("work_experience_min_years")
            or rule.get("minimum_work_experience_years")
        )

        if required_years is not None:
            if years is None:
                missing.append("Work experience not provided")
                penalties += 1
            elif years < required_years:
                missing.append(
                    f"Insufficient work experience ({years} years, need {required_years})"
                )
                penalties += 1

        # Calculate final score
        score = max(0.0, 1.0 - penalties / self.MAX_PENALTIES)

        # Determine status
        if score >= self.SCORE_OK:
            status = "OK"
        elif score >= self.SCORE_BORDERLINE:
            status = "Borderline"
        else:
            status = "High Risk"

        # Build gaps structure
        gaps: Dict[str, Any] = {
            "missing_requirements": missing,
            "risk_status": "Risk" if risks else "No Risk",
        }
        if risks:
            gaps["risks"] = risks

        return status, score, gaps

    def evaluate_all(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate profile against all rules.

        Args:
            profile: User profile dict

        Returns:
            List of MatchResult dicts
        """
        if not profile:
            raise ValueError("Profile cannot be empty")

        # ---- Logging (خیلی کوتاه و safe) ----
        if self.logger:
            self.logger.log_agent_call(
                agent_name="MatchAgent",
                session_id=None,
                input_summary=str({
                    "goal": profile.get("goal"),
                    "age": profile.get("age"),
                    "citizenship": profile.get("citizenship"),
                })[:160],
            )

        goal = profile.get("goal")
        results: List[Dict[str, Any]] = []

        for rule in self.rules:
            pathway = rule.get("pathway")

            # Filter by goal if specified
            if goal and pathway and pathway.lower() != goal.lower():
                continue

            try:
                status, score, gaps = self._score_single_rule(profile, rule)

                result = {
                    "country": rule.get("country"),
                    "pathway": pathway,
                    "status": status,
                    "raw_score": score,
                    "rule_gaps": gaps,
                }
                results.append(result)
            except Exception as e:
                # Use logger instead of print
                if self.logger:
                    self.logger.log_exception(
                        error=e,
                        context=f"MatchAgent evaluating {rule.get('country')}/{pathway}",
                    )
                continue

        return results
