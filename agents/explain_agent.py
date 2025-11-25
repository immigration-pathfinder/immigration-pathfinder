from typing import Any, Dict, Optional
from tools.logger import Logger


class ExplainAgent:
    """
    ExplainAgent

    Takes a match_result (e.g., eligible / not-eligible countries)
    and generates a human-readable explanation for the user.

    Phase 3:
        - We only care about logging + a simple mock explanation
        - Real LLM / Gemini logic can be added later in Kaggle notebook
    """

    def __init__(self, logger: Optional[Logger] = None) -> None:
        # Use shared Logger instance if provided, otherwise create a default one
        self.logger = logger or Logger()

    def run(
        self,
        user_profile: Dict[str, Any],
        match_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate a user-facing explanation for the match_result.

        Expected inputs (loosely):
            user_profile: structured dict from ProfileAgent
            match_result: dict from MatchAgent (eligible_countries, reasoning, ...)

        Returns a dict that could be shown to the user or passed to the UI layer:
            {
                "summary": str,
                "eligible_countries": List[str],
                "details": str,
            }
        """

        # -----------------------------
        # Logging (Phase 3)
        # -----------------------------
        if self.logger:
            self.logger.log_agent_call(
                agent_name="ExplainAgent",
                session_id=None,
                input_summary=str({
                    "profile_keys": list(user_profile.keys()),
                    "match_keys": list(match_result.keys()),
                })[:200],
            )

        eligible = match_result.get("eligible_countries", []) or []
        reasoning = match_result.get("reasoning", "No detailed reasoning provided.")

        if eligible:
            summary = f"You may be eligible for {len(eligible)} country(ies)."
            details = (
                "Based on your profile, the system found potential options: "
                + ", ".join(eligible)
                + ". "
                + f"Reasoning: {reasoning}"
            )
        else:
            summary = "No eligible countries were found with the current rules."
            details = (
                "The current rule set did not find a clear path for your profile. "
                "You may need to improve language scores, funds, or experience. "
                f"Reasoning: {reasoning}"
            )

        return {
            "summary": summary,
            "eligible_countries": eligible,
            "details": details,
        }


if __name__ == "__main__":
    # Minimal local test for Phase 3
    sample_profile = {
        "age": 32,
        "citizenship": "Iran",
        "goal": "Work",
    }

    sample_match = {
        "eligible_countries": ["Germany", "Netherlands"],
        "reasoning": "Profile matches basic work visa requirements.",
    }

    agent = ExplainAgent()
    result = agent.run(sample_profile, sample_match)
    print(result)

