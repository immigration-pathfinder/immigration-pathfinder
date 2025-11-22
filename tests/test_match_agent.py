# tests/test_match_agent_manual.py
import json
from agents.match_agent import MatchAgent


def run_manual_test():
    print("\nRunning Manual Test for MatchAgent...\n")

    # --------------------------
    # Test Profile (valid sample)
    # --------------------------
    profile = {
        "age": 27,
        "citizenship": "Iran",
        "marital_status": "single",
        "education_level": "bachelor",
        "field": "electrical_engineering",
        "ielts": 6.5,
        "german_level": "none",
        "french_level": "none",
        "funds_usd": 18000,
        "work_experience_years": 3,
        "goal": "Study",
        "preferred_region": ["Europe", "North America"],
    }

    # --------------------------
    # Load Rules
    # --------------------------
    with open("rules/country_rules.json", "r", encoding="utf-8") as f:
        rules_list = json.load(f)

    # --------------------------
    # Initialize
    # --------------------------
    agent = MatchAgent(rules_list)
    results = agent.evaluate_all(profile)

    # --------------------------
    # Print test summary
    # --------------------------
    print("Total Results Returned:", len(results))
    print(json.dumps(results, indent=2, ensure_ascii=False))

    # --------------------------
    # Assertions (Basic Checks)
    # --------------------------
    assert isinstance(results, list), "Results must be a list"
    assert len(results) > 0, "No results returned from MatchAgent"

    for item in results:
        assert "country" in item, "Missing 'country' key"
        assert "pathway" in item, "Missing 'pathway' key"
        assert "status" in item, "Missing 'status' key"
        assert "raw_score" in item, "Missing 'raw_score' key"
        assert "rule_gaps" in item, "Missing 'rule_gaps' key"

        gaps = item["rule_gaps"]

        assert "missing_requirements" in gaps, "Missing 'missing_requirements' in rule_gaps"
        assert "risk_status" in gaps, "Missing 'risk_status' in rule_gaps"

        # If risk exists, risks list must be present
        if gaps["risk_status"] == "Risk":
            assert "risks" in gaps, "'risks' should exist when risk_status = Risk"
            assert isinstance(gaps["risks"], list), "'risks' must be a list"

    print("\n Manual Test Passed Successfully!\n")


if __name__ == "__main__":
    run_manual_test()
