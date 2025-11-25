from typing import Any, Dict, Optional

from tools.logger import Logger
from agents.profile_agent import ProfileAgent
from agents.match_agent import MatchAgent


class Orchestrator:
    """
    Orchestrator

    Controls the full pipeline:
    1. Convert raw user text to structured profile (ProfileAgent)
    2. Match structured profile to countries (MatchAgent)
    """

    def __init__(self, logger: Optional[Logger] = None) -> None:
        # Create a default logger if none is provided
        self.logger = logger or Logger()

        # Initialize sub-agents
        self.profile_agent = ProfileAgent(logger=self.logger)
        self.match_agent = MatchAgent(logger=self.logger)

    def run(self, raw_text: str) -> Dict[str, Any]:
        """
        End-to-end pipeline:
        1. Profile extraction
        2. Matching
        """

        # Log incoming raw text
        if self.logger:
            self.logger.log_agent_call(
                agent_name="Orchestrator",
                session_id=None,
                input_summary=raw_text[:200],
            )

        # Step 1: Build structured profile
        profile = self.profile_agent.run(raw_text)

        # Step 2: Evaluate the profile for countries
        match_result = self.match_agent.run(profile)

        # Log final summary
        if self.logger:
            self.logger.log_tool_call(
                tool_name="OrchestratorFinal",
                params={
                    "profile_keys": list(profile.keys()),
                    "eligible_countries": match_result.get("eligible_countries", []),
                },
            )

        return {
            "profile": profile,
            "match_result": match_result,
        }


if __name__ == "__main__":
    orch = Orchestrator()
    text = "I'm a 32 years old Iranian looking for work in Europe."
    out = orch.run(text)
    print(out)

