from typing import Any, Dict, Optional

from tools.logger import Logger
from agents.profile_agent import ProfileAgent
from agents.match_agent import MatchAgent
from agents.country_finder_agent import CountryFinderAgent
from agents.explain_agent import ExplainAgent


class Orchestrator:
    """
    Orchestrator

    Controls the full pipeline:
    1. Convert raw user text to structured profile (ProfileAgent)
    2. Match structured profile to countries (MatchAgent)
    3. Pick the best country (CountryFinderAgent)
    4. Generate a human-readable explanation (ExplainAgent)
    """

    def __init__(self, logger: Optional[Logger] = None) -> None:
        # Create a default logger if none is provided
        self.logger = logger or Logger()

        # Initialize sub-agents
        self.profile_agent = ProfileAgent(logger=self.logger)
        self.match_agent = MatchAgent(logger=self.logger)
        self.country_finder = CountryFinderAgent(logger=self.logger)
        self.explain_agent = ExplainAgent(logger=self.logger)

    def run(self, raw_text: str) -> Dict[str, Any]:
        """
        End-to-end pipeline:
        1. Profile extraction
        2. Matching
        3. Country recommendation
        4. Explanation
        """

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

        # Step 3: Recommend the best country
        recommended_country = self.country_finder.run(match_result)

        # Step 4: Generate explanation (positional args)
        explanation = self.explain_agent.run(
            profile,
            match_result,
        )


        if self.logger:
            self.logger.log_tool_call(
                tool_name="OrchestratorFinal",
                params={
                    "profile_keys": list(profile.keys()),
                    "eligible_countries": match_result.get("eligible_countries", []),
                    "recommended_country": recommended_country,
                },
            )

        return {
            "profile": profile,
            "match_result": match_result,
            "recommended_country": recommended_country,
            "explanation": explanation,
        }


if __name__ == "__main__":
    orch = Orchestrator()
    text = """
    I am 30 years old and from Iran.
    I have a bachelor degree in computer engineering.
    I have 2 years of work experience.
    My English level is B1.
    I have 10000 USD savings.
    My goal is work.
    My target countries are Germany and Netherlands.
    """
    out = orch.run(text)

    import json
    print(json.dumps(out, indent=4, ensure_ascii=False))
