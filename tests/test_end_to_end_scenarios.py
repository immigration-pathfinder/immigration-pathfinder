import pytest

from agents.orchestrator import Orchestrator


SCENARIOS = [
    {
        "name": "student_low_budget_europe",
        "input": (
            "I am 24 years old, from Iran. I want to do a Master's in Computer Science "
            "in Europe with low tuition. My budget is very limited and I prefer countries "
            "where I can study in English. Please suggest immigration paths and countries."
        ),
    },
    {
        "name": "skilled_worker_it",
        "input": (
            "I am a 32-year-old software engineer with 8 years of experience. "
            "I want to immigrate permanently to an English-speaking country with "
            "good salaries and a clear work visa or PR pathway."
        ),
    },
    {
        "name": "family_reunification",
        "input": (
            "My spouse recently obtained permanent residency in another country, "
            "and I want to join them through a family reunification or spouse visa. "
            "Please explain possible paths."
        ),
    },
    {
        "name": "refugee_humanitarian",
        "input": (
            "I am at serious risk in my home country due to political persecution. "
            "I need information about asylum or humanitarian protection options."
        ),
    },
    {
        "name": "entrepreneur_startup",
        "input": (
            "I have savings and want to start a tech startup abroad. "
            "I am looking for countries that have startup or entrepreneur visa programs."
        ),
    },
    {
        "name": "retiree_low_cost",
        "input": (
            "I am 65 years old, have a stable pension, and want to retire in a safe country "
            "with relatively low cost of living and mild climate."
        ),
    },
]


def run_pipeline(user_message: str):
    """
    Helper to run the full Immigration Pathfinder pipeline using the real Orchestrator.
    """
    orch = Orchestrator()
    result = orch.run(user_message)
    return result


@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s["name"] for s in SCENARIOS])
def test_end_to_end_scenarios(scenario):
    result = run_pipeline(scenario["input"])

    assert isinstance(result, dict), "Result should be a dict"

    assert "profile" in result
    assert "match_results" in result
    assert "ranking" in result
    assert "recommended_country" in result
    assert "explanation" in result

    explanation = str(result["explanation"]).strip()
    assert len(explanation) > 0, "Explanation should not be empty."


    if scenario["name"] != "refugee_humanitarian":
        assert result["recommended_country"] is not None, "Expected a recommended_country"

    lowered = explanation.lower()

    if scenario["name"] == "student_low_budget_europe":
        assert (
            "tuition" in lowered
            or "budget" in lowered
            or "cost" in lowered
        ), "Student scenario should mention cost/tuition/budget."

    if scenario["name"] == "skilled_worker_it":
        assert (
            "work visa" in lowered
            or "skilled" in lowered
            or "job" in lowered
        ), "Skilled worker scenario should mention work visa / job."

    if scenario["name"] == "family_reunification":
        assert (
            "family" in lowered
            or "spouse" in lowered
        ), "Family scenario should mention family/spouse."

    if scenario["name"] == "refugee_humanitarian":
        assert (
            "asylum" in lowered
            or "legal" in lowered
            or "lawyer" in lowered
            or "official" in lowered
        ), "Refugee scenario should mention asylum/official/legal guidance."

    if scenario["name"] == "entrepreneur_startup":
        assert (
            "startup" in lowered
            or "entrepreneur" in lowered
            or "business" in lowered
        ), "Entrepreneur scenario should mention startup/entrepreneur/business."

    if scenario["name"] == "retiree_low_cost":
        assert (
            "retire" in lowered
            or "retirement" in lowered
            or "cost of living" in lowered
        ), "Retiree scenario should mention retirement / cost of living."
