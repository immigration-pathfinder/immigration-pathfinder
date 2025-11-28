from agents.profile_agent import ProfileAgent


def test_manual_run():
    agent = ProfileAgent()

    text = "I'm a 32 years old Iranian, single, looking for work in Europe. IELTS 6.5, 5 years work experience, 15000 USD savings."

    profile = agent.run(text)
    print("PROFILE OUTPUT:", profile)
    print("PROFILE KEYS:", profile.keys())
