from typing import Any, Dict, List, Optional
from tools.logger import Logger


class CountryFinderAgent:
    """
    CountryFinderAgent

    Phase 3 scope:
        - Takes a normalized user_profile (dict)
        - Returns a simple mock list of eligible countries + reasoning
        - Logs the call via shared Logger

    Real matching logic (funds, language, experience, etc.)
    will be implemented later in Phase 4 / Kaggle notebooks.
    """

    def __init__(self, logger: Optional[Logger] = None) -> None:
        # Use shared logger if provided, otherwise create a default one
        self.logger = logger or Logger()

    def run(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point.

        Input:
            user_profile: dict from ProfileAgent / orchestrator
                expected keys (loosely):
                    - goal
                    - citizenship
                    - target_countries
                    - english_level / english_score
                    - funds_usd
                    - work_experience_years

        Output:
            {
                "eligible_countries": List[str],
                "reasoning": str
            }
        """

        # -----------------------------
        # Logging (Phase 3)
        # -----------------------------
        if self.logger:
            self.logger.log_agent_call(
                agent_name="CountryFinderAgent",
                session_id=None,
                input_summary=str({
                    "citizenship": user_profile.get("citizenship"),
                    "goal": user_profile.get("goal"),
                    "target_countries": user_profile.get("target_countries"),
                })[:200],
            )

        # -----------------------------
        # Mock matching logic (placeholder)
        # -----------------------------
        goal = (user_profile.get("goal") or "").lower()
        citizenship = (user_profile.get("citizenship") or "").title()
        target_countries: List[str] = user_profile.get("target_countries") or []

        eligible: List[str] = []
        reasoning_parts: List[str] = []

        if goal == "work":
            reasoning_parts.append("User goal is work migration.")
        elif goal == "study":
            reasoning_parts.append("User goal is study abroad.")
        elif goal == "pr":
            reasoning_parts.append("User goal is permanent residency.")
        else:
            reasoning_parts.append("User goal is unclear in the profile.")

        if target_countries:
            # For now, just echo target_countries as mock 'eligible'
            eligible = target_countries
            reasoning_parts.append(
                f"Using target_countries from profile as potential options: {', '.join(target_countries)}."
            )
        else:
            reasoning_parts.append(
                "No target_countries were specified; no mock eligibility assigned."
            )

        if not eligible:
            reasoning_parts.append(
                "CountryFinderAgent in Phase 3 only returns target_countries as eligible; "
                "since none were provided, the list is empty."
            )

        reasoning = " ".join(reasoning_parts)

        return {
            "eligible_countries": eligible,
            "reasoning": reasoning,
        }


if __name__ == "__main__":
    # Minimal local test for Phase 3
    sample_profile = {
        "age": 32,
        "citizenship": "Iran",
        "goal": "Work",
        "target_countries": ["Germany", "Netherlands"],
        "funds_usd": 15000,
        "work_experience_years": 5,
    }

    agent = CountryFinderAgent()
    result = agent.run(sample_profile)
    print(result)

