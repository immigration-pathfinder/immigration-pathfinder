from typing import Any, Dict, Optional
from tools.logger import Logger


class MatchAgent:
    """
    MatchAgent

    Takes a structured user profile and evaluates it against
    immigration rules for each country.

    For Phase 3, we only add logging hooks and a placeholder result.
    """

    def __init__(self, logger: Optional[Logger] = None) -> None:
        # Create a default logger if none is provided
        self.logger = logger or Logger()

    def run(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry for matching user profile to immigration rules.
        For Phase 3 we only add logging; real logic will be added in Phase 4.
        """

        # Log the call
        if self.logger:
            self.logger.log_agent_call(
                agent_name="MatchAgent",
                session_id=None,
                input_summary=str(user_profile)[:200],
            )

        # Placeholder output (Phase 4 will replace this)
        result = {
            "eligible_countries": [],
            "reasoning": "Matching logic not implemented yet."
        }

        return result


if __name__ == "__main__":
    # Temporary test (manual run)
    agent = MatchAgent()
    test_profile = {
        "age": 32,
        "citizenship": "Iran",
        "goal": "Work",
        "education_level": "Master"
    }

    output = agent.run(test_profile)
    print(output)
