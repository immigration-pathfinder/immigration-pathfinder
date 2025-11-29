# tests/test_match_agent.py
import sys
from pathlib import Path

# IMPORTANT: Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import json
from agents.match_agent import MatchAgent


# Find rules path
RULES_PATH = PROJECT_ROOT / "rules" / "country_rules.json"


def load_rules():
    """Load country rules from JSON file."""
    try:
        with open(RULES_PATH, "r", encoding="utf-8") as f:
            rules_list = json.load(f)
        print(f"[INFO] Loaded {len(rules_list)} rules from {RULES_PATH}")
        return rules_list
    except FileNotFoundError:
        print(f"[ERROR] File not found: {RULES_PATH}")
        print("        Make sure you run this from project root or create the file.")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in {RULES_PATH}")
        print(f"        {e}")
        exit(1)


def print_results_summary(results):
    """Print a nice summary of results."""
    print("\n" + "=" * 60)
    print(f"RESULTS SUMMARY: {len(results)} matches found")
    print("=" * 60)

    # Group by status
    by_status = {"OK": [], "Borderline": [], "High Risk": []}
    for r in results:
        by_status[r["status"]].append(r)

    for status in ["OK", "Borderline", "High Risk"]:
        count = len(by_status[status])
        print(f"\n[{status}]: {count} countries")

        for result in by_status[status][:3]:
            print(
                f"   - {result['country']} ({result['pathway']}): "
                f"Score {result['raw_score']:.2f}"
            )

            gaps = result["rule_gaps"]["missing_requirements"]
            if gaps:
                print(f"     Gaps: {gaps[0]}")
                if len(gaps) > 1:
                    print(f"           + {len(gaps)-1} more...")


# --------------------------------------------------------------------
# Scenario helpers (return results so run_all_tests can use them)
# --------------------------------------------------------------------


def _scenario_valid_profile():
    """Scenario 1: complete, valid profile."""
    print("\n" + "=" * 60)
    print("TEST 1: Valid Student Profile")
    print("=" * 60)

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

    rules_list = load_rules()
    agent = MatchAgent(rules_list)
    results = agent.evaluate_all(profile)

    # Assertions
    assert isinstance(results, list), "Results must be a list"
    assert len(results) > 0, "No results returned"

    for item in results:
        assert "country" in item, "Missing 'country' key"
        assert "pathway" in item, "Missing 'pathway' key"
        assert "status" in item, "Missing 'status' key"
        assert "raw_score" in item, "Missing 'raw_score' key"
        assert "rule_gaps" in item, "Missing 'rule_gaps' key"

        gaps = item["rule_gaps"]
        assert "missing_requirements" in gaps, "Missing 'missing_requirements'"
        assert "risk_status" in gaps, "Missing 'risk_status'"

        if gaps["risk_status"] == "Risk":
            assert "risks" in gaps, "'risks' should exist when risk_status = Risk"
            assert isinstance(gaps["risks"], list), "'risks' must be a list"

    print_results_summary(results)
    print("[PASS] Test 1 Passed")
    return results


def _scenario_low_funds_profile():
    """Scenario 2: insufficient funds."""
    print("\n" + "=" * 60)
    print("TEST 2: Low Funds Profile")
    print("=" * 60)

    profile = {
        "age": 25,
        "citizenship": "Iran",
        "education_level": "bachelor",
        "ielts": 6.0,
        "funds_usd": 5000,
        "work_experience_years": 1,
        "goal": "Study",
    }

    rules_list = load_rules()
    agent = MatchAgent(rules_list)
    results = agent.evaluate_all(profile)

    high_risk_count = sum(1 for r in results if r["status"] == "High Risk")
    print(f"\n[INFO] High Risk matches: {high_risk_count}")

    assert len(results) > 0, "Should return results even with low funds"
    print_results_summary(results)
    print("[PASS] Test 2 Passed")
    return results


def _scenario_missing_fields():
    """Scenario 3: minimal profile (missing optional fields)."""
    print("\n" + "=" * 60)
    print("TEST 3: Minimal Profile (Missing Fields)")
    print("=" * 60)

    profile = {
        "age": 30,
        "education_level": "master",
        "goal": "Work",
    }

    rules_list = load_rules()
    agent = MatchAgent(rules_list)
    results = agent.evaluate_all(profile)

    assert len(results) > 0, "Should handle missing fields gracefully"

    for r in results[:3]:
        gaps = r["rule_gaps"]["missing_requirements"]
        print(f"\n{r['country']}: {len(gaps)} gaps detected")
        for gap in gaps[:2]:
            print(f"   - {gap}")

    print("[PASS] Test 3 Passed")
    return results


def _scenario_all_pathways():
    """Scenario 4: filtering by different pathways."""
    print("\n" + "=" * 60)
    print("TEST 4: Different Pathways")
    print("=" * 60)

    rules_list = load_rules()
    agent = MatchAgent(rules_list)

    base_profile = {
        "age": 28,
        "education_level": "bachelor",
        "ielts": 7.0,
        "funds_usd": 20000,
        "work_experience_years": 4,
    }

    for goal in ["Study", "Work", "PR"]:
        profile = {**base_profile, "goal": goal}
        results = agent.evaluate_all(profile)

        for r in results:
            assert (
                r["pathway"] == goal
            ), f"Pathway mismatch: expected {goal}, got {r['pathway']}"

        print(f"\n{goal}: {len(results)} matches")

    print("[PASS] Test 4 Passed")


# --------------------------------------------------------------------
# Pytest-facing test functions (must return None)
# --------------------------------------------------------------------


def test_valid_profile():
    _scenario_valid_profile()


def test_low_funds_profile():
    _scenario_low_funds_profile()


def test_missing_fields():
    _scenario_missing_fields()


def test_all_pathways():
    _scenario_all_pathways()


# --------------------------------------------------------------------
# Manual runner
# --------------------------------------------------------------------


def run_all_tests():
    """Run all manual tests."""
    print("\n" + "=" * 60)
    print("STARTING MATCH AGENT TESTS")
    print("=" * 60)

    try:
        _scenario_valid_profile()
        _scenario_low_funds_profile()
        _scenario_missing_fields()
        _scenario_all_pathways()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED")
        print("=" * 60 + "\n")

    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}\n")
        exit(1)
    except Exception as e:
        print(f"\n[ERROR] UNEXPECTED ERROR: {e}\n")
        import traceback

        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    run_all_tests()
