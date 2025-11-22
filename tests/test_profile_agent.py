from agents.profile_agent import ProfileAgent, USER_PROFILE_FIELDS


def test_profile_agent_returns_valid_profile_structure():
    agent = ProfileAgent()
    text = "I am 32 years old from Iran, married, master's in data science, 7 years of experience, want to work in Europe."
    profile = agent.run(text)

    assert isinstance(profile, dict), "ProfileAgent.run() must return a dict"

    for key in profile.keys():
        assert key in USER_PROFILE_FIELDS, f"Unexpected field in profile: {key}"


def test_normalize_profile_trims_and_normalizes_fields():
    agent = ProfileAgent()

    raw_profile = {
        "citizenship": " germany ",
        "preferred_region": [" europe ", "  North america  "],
        "field": "  data science  "
    }

    normalized = agent._normalize_profile(raw_profile)

    assert normalized["citizenship"] == "Germany"
    assert normalized["field"] == "data science"
    assert normalized["preferred_region"] == ["europe", "North america"]

