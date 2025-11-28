import unittest
from memory.session_service import SessionService
from schemas.user_profile import UserProfile, PersonalInfo, Education, WorkExperience, LanguageProficiency, FinancialInfo
from schemas.country_ranking import CountryRanking, RankedCountry

class TestSessionService(unittest.TestCase):

    def setUp(self):
        self.session_service = SessionService()
        self.user_profile_data = UserProfile(
            personal_info=PersonalInfo(
                first_name="Jane",
                last_name="Doe",
                age=25,
                nationality="French",
                current_residence="France",
                marital_status="single"
            ),
            education=Education(
                degree_level="master",
                field_of_study="Data Science"
            ),
            work_experience=WorkExperience(
                occupation="Data Scientist",
                years_of_experience=3
            ),
            language_proficiency=LanguageProficiency(
                ielts_score=7.5
            ),
            financial_info=FinancialInfo(
                liquid_assets_usd=30000
            ),
            immigration_goal="Work",
            preferred_countries=["Canada"]
        )
        self.country_ranking_data = CountryRanking(
            ranked_countries=[
                RankedCountry(country="Canada", pathway="Work", score=95, reason="High demand for data scientists")
            ]
        )

    def test_session_creation_works(self):
        session_id = "user123"
        user_profile = self.session_service.get_user_profile(session_id)
        self.assertIsNone(user_profile)
        self.session_service.update_user_profile(session_id, self.user_profile_data)
        retrieved_profile = self.session_service.get_user_profile(session_id)
        self.assertEqual(retrieved_profile, self.user_profile_data)

    def test_profile_updates_merge_correctly(self):
        session_id = "user123"
        self.session_service.update_user_profile(session_id, self.user_profile_data)
        updated_profile_data = UserProfile(
            personal_info=PersonalInfo(
                first_name="Jane",
                last_name="Doe",
                age=26, # Updated age
                nationality="French",
                current_residence="France",
                marital_status="single"
            ),
            education=Education(
                degree_level="master",
                field_of_study="Data Science"
            ),
            work_experience=WorkExperience(
                occupation="Senior Data Scientist", # Updated occupation
                years_of_experience=4 # Updated years of experience
            ),
            language_proficiency=LanguageProficiency(
                ielts_score=8.0 # Updated IELTS score
            ),
            financial_info=FinancialInfo(
                liquid_assets_usd=35000 # Updated liquid assets
            ),
            immigration_goal="Work",
            preferred_countries=["Canada", "Australia"] # Updated preferred countries
        )
        self.session_service.update_user_profile(session_id, updated_profile_data)
        retrieved_profile = self.session_service.get_user_profile(session_id)
        self.assertEqual(retrieved_profile, updated_profile_data)

    def test_recommendations_are_stored(self):
        session_id = "user123"
        self.session_service.update_country_ranking(session_id, self.country_ranking_data)
        retrieved_ranking = self.session_service.get_country_ranking(session_id)
        self.assertEqual(retrieved_ranking, self.country_ranking_data)

    def test_reset_clears_data(self):
        session_id = "user123"
        self.session_service.update_user_profile(session_id, self.user_profile_data)
        self.session_service.update_country_ranking(session_id, self.country_ranking_data)
        self.session_service.reset_session(session_id)
        user_profile = self.session_service.get_user_profile(session_id)
        country_ranking = self.session_service.get_country_ranking(session_id)
        self.assertIsNone(user_profile)
        self.assertIsNone(country_ranking)

    def test_multiple_users_do_not_conflict(self):
        session_id_1 = "user1"
        session_id_2 = "user2"

        user_profile_1 = self.user_profile_data
        country_ranking_1 = self.country_ranking_data

        user_profile_2 = UserProfile(
            personal_info=PersonalInfo(
                first_name="Mark",
                last_name="Smith",
                age=35,
                nationality="German",
                current_residence="Germany",
                marital_status="married"
            ),
            education=Education(
                degree_level="phd",
                field_of_study="Physics"
            ),
            work_experience=WorkExperience(
                occupation="Researcher",
                years_of_experience=10
            ),
            language_proficiency=LanguageProficiency(
                ielts_score=6.0,
                german_level="c1"
            ),
            financial_info=FinancialInfo(
                liquid_assets_usd=70000
            ),
            immigration_goal="PR",
            preferred_countries=["Germany"]
        )
        country_ranking_2 = CountryRanking(
            ranked_countries=[
                RankedCountry(country="Germany", pathway="PR", score=98, reason="Excellent research opportunities")
            ]
        )

        self.session_service.update_user_profile(session_id_1, user_profile_1)
        self.session_service.update_country_ranking(session_id_1, country_ranking_1)

        self.session_service.update_user_profile(session_id_2, user_profile_2)
        self.session_service.update_country_ranking(session_id_2, country_ranking_2)

        retrieved_profile_1 = self.session_service.get_user_profile(session_id_1)
        retrieved_ranking_1 = self.session_service.get_country_ranking(session_id_1)
        retrieved_profile_2 = self.session_service.get_user_profile(session_id_2)
        retrieved_ranking_2 = self.session_service.get_country_ranking(session_id_2)

        self.assertEqual(retrieved_profile_1, user_profile_1)
        self.assertEqual(retrieved_ranking_1, country_ranking_1)
        self.assertEqual(retrieved_profile_2, user_profile_2)
        self.assertEqual(retrieved_ranking_2, country_ranking_2)

if __name__ == '__main__':
    unittest.main()
