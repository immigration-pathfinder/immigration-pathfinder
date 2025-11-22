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
    assert isinstance(results, list)
    assert len(results) > 0  # Should return at least some matching pathways

    for item in results:
        assert "country" in item
        assert "pathway" in item
        assert "status" in item
        assert "raw_score" in item
        assert "rule_gaps" in item
        assert "missing_requirements" in item["rule_gaps"]

    print("\n Manual Test Passed Successfully!\n")


if __name__ == "__main__":
    run_manual_test()
