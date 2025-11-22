# agents/match_agent.py
from typing import List, Dict, Any

DEGREE_ORDER = {
    "high_school": 0,
    "diploma": 1,
    "bachelor": 2,
    "master": 3,
    "phd": 4,
}


class MatchAgent:
    """
    Compare a flat UserProfile dict against a list of country/pathway rules
    and produce a list of MatchResult dicts.
    """

    def __init__(self, rules: List[Dict[str, Any]]) -> None:
        """
        Args:
            rules: List of rule dicts loaded from country_rules.json
        """
        self.rules = rules or []

    def _score_single_rule(
        self,
        profile: Dict[str, Any],
        rule: Dict[str, Any],
    ) -> (str, float, Dict[str, Any]):
        """
        Compare one user profile against one rule.

        Returns:
            status: "OK" | "Borderline" | "High Risk"
            score: float in [0, 1]
            gaps: {"missing_requirements": [...], "risk_status": "...", "risks"?: [...]}
        """
        missing: List[str] = []
        risks: List[str] = []
        penalties = 0
        max_penalties = 5  # tune later if needed

        # ----- Age -----
        age = profile.get("age")
        min_age = rule.get("minimum_age")
        max_age = rule.get("maximum_age") or rule.get("age_max")

        if age is not None:
            if min_age is not None and age < min_age:
                missing.append("Age below minimum requirement")
                penalties += 1
            if max_age is not None and age > max_age:
                missing.append("Age above maximum limit")
                penalties += 1

        # ----- Degree level -----
        profile_degree = profile.get("education_level")
        required_degree = rule.get("min_degree") or rule.get("minimum_degree")
        if profile_degree and required_degree:
            profile_rank = DEGREE_ORDER.get(profile_degree, -1)
            required_rank = DEGREE_ORDER.get(required_degree, -1)
            if profile_rank < required_rank:
                missing.append(
                    f"Degree '{profile_degree}' below required '{required_degree}'"
                )
                penalties += 1

        # ----- IELTS / English level -----
        profile_ielts = profile.get("ielts")
        required_ielts = rule.get("min_ielts") or rule.get("minimum_ielts")

        if required_ielts is not None and profile_ielts is not None:
            if profile_ielts < required_ielts:
                missing.append(
                    f"IELTS score {profile_ielts} below required {required_ielts}"
                )
                penalties += 1

        # ----- Funds / income -----
        funds = profile.get("funds_usd")
        required_funds = (
            rule.get("min_funds_usd")
            or rule.get("minimum_funds_usd")
            or rule.get("minimum_income_usd")
        )

        if required_funds is not None and funds is not None:
            if funds < required_funds:
                missing.append(
                    f"Insufficient funds (needs ≥ {required_funds} USD)"
                )
                penalties += 1
                # example: mark as a risk if funds gap is big
                if required_funds - funds > 5000:
                    risks.append("Large funds gap may increase visa refusal risk")

        # ----- Work experience -----
        years = profile.get("work_experience_years")
        required_years = (
            rule.get("work_experience_min_years")
            or rule.get("minimum_work_experience_years")
        )

        if required_years is not None and years is not None:
            if years < required_years:
                missing.append(
                    f"Not enough work experience (needs {required_years} years)"
                )
                penalties += 1

        # ----- Final score & status -----
        if max_penalties > 0:
            score = max(0.0, 1.0 - penalties / max_penalties)
        else:
            score = 1.0

        if score >= 0.75:
            status = "OK"
        elif score >= 0.4:
            status = "Borderline"
        else:
            status = "High Risk"

        # ----- Build gaps structure with risk status -----
        if risks:
            risk_status = "Risk"
        else:
            risk_status = "No Risk"

        gaps: Dict[str, Any] = {
            "missing_requirements": missing,
            "risk_status": risk_status,
        }
        if risks:
            gaps["risks"] = risks

        return status, score, gaps

    def evaluate_all(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate the profile against all rules.

        - If profile["goal"] is set, only rules with matching pathway are considered.
        - Returns a list of MatchResult dicts.
        """
        goal = profile.get("goal")
        results: List[Dict[str, Any]] = []

        for rule in self.rules:
            pathway = rule.get("pathway")

            # If user has a goal, filter by pathway
            if goal and pathway and pathway.lower() != goal.lower():
                continue

            status, score, gaps = self._score_single_rule(profile, rule)

            result = {
                "country": rule.get("country"),
                "pathway": pathway,
                "status": status,
                "raw_score": score,
                "rule_gaps": gaps,
            }
            results.append(result)

        return results
