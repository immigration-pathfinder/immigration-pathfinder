import unittest
from unittest.mock import Mock
from agents.explain_agent import ExplainAgent
from schemas.user_profile import UserProfile, PersonalInfo, Education, WorkExperience, LanguageProficiency, FinancialInfo
from schemas.country_ranking import CountryRanking, RankedCountry
from memory.session_service import SessionService
from tools.search_tool import SearchTool

class TestExplainAgent(unittest.TestCase):

    def setUp(self):
        self.mock_session_service = Mock(spec=SessionService)
        self.mock_search_tool = Mock(spec=SearchTool)
        self.explain_agent = ExplainAgent(self.mock_session_service, self.mock_search_tool)

        self.user_profile_data = UserProfile(
            personal_info=PersonalInfo(
                first_name="John",
                last_name="Doe",
                age=30,
                nationality="Iranian",
                current_residence="Iran",
                marital_status="single"
            ),
            education=Education(
                degree_level="bachelor",
                field_of_study="Computer Science"
            ),
            work_experience=WorkExperience(
                occupation="Software Engineer",
                years_of_experience=5
            ),
            language_proficiency=LanguageProficiency(
                ielts_score=7.0
            ),
            financial_info=FinancialInfo(
                liquid_assets_usd=50000
            ),
            immigration_goal="PR",
            preferred_countries=["Canada", "Germany"]
        )

        self.country_ranking_data = CountryRanking(
            ranked_countries=[
                RankedCountry(country="Canada", pathway="Work", score=90, reason="High demand for software engineers"),
                RankedCountry(country="Germany", pathway="PR", score=85, reason="Good job market and integration programs")
            ]
        )

        self.empty_country_ranking = CountryRanking(
            ranked_countries=[]
        )

    def test_explanation_not_empty(self):
        explanation = self.explain_agent.generate_explanation(self.user_profile_data, self.country_ranking_data)
        self.assertIsInstance(explanation, str)
        self.assertTrue(len(explanation) > 0)

    def test_explanation_mentions_top_countries(self):
        explanation = self.explain_agent.generate_explanation(self.user_profile_data, self.country_ranking_data)
        self.assertIn("Canada", explanation)
        self.assertIn("Germany", explanation)

    def test_handles_no_recommendations(self):
        explanation = self.explain_agent.generate_explanation(self.user_profile_data, self.empty_country_ranking)
        self.assertIn("no specific country recommendations", explanation)

    # This test would require a mock for the Gemini API to simulate its unavailability
    # For now, we'll assume the fallback is called if an exception occurs.
    def test_fallback_on_gemini_failure(self):
        # Simulate Gemini API failure by making _generate_explanation_with_gemini raise an exception
        self.explain_agent._generate_explanation_with_gemini = Mock(side_effect=Exception("Gemini API error"))
        explanation = self.explain_agent.generate_explanation(self.user_profile_data, self.country_ranking_data)
        self.assertIn("Dear John", explanation) # Check for a string specific to the fallback template
        self.assertIn("Canada - Work Pathway", explanation)

if __name__ == '__main__':
    unittest.main()
