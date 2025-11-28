import json
from typing import List, Dict, Any

from memory.session_service import SessionService
from tools.search_tool import SearchTool
from schemas.user_profile import UserProfile, PersonalInfo, Education, WorkExperience, LanguageProficiency, FinancialInfo
from schemas.country_ranking import CountryRanking, RankedCountry

class ExplainAgent:
    def __init__(self, session_service: SessionService, search_tool: SearchTool):
        self.session_service = session_service
        self.search_tool = search_tool
        # Initialize Gemini API here if needed, or pass it as a dependency

    def generate_explanation(self, user_profile: UserProfile, country_ranking: CountryRanking) -> str:
        # Placeholder for Gemini API call
        try:
            # Attempt to use Gemini API
            explanation = self._generate_explanation_with_gemini(user_profile, country_ranking)
        except Exception as e:
            print(f"Gemini API unavailable or failed: {e}. Using fallback template.")
            explanation = self._generate_fallback_explanation(user_profile, country_ranking)
        
        return explanation

    def _generate_explanation_with_gemini(self, user_profile: UserProfile, country_ranking: CountryRanking) -> str:
        # This is where the actual Gemini API call would go.
        # For now, it's a placeholder.
        # You would construct a prompt using user_profile and country_ranking
        # and send it to the Gemini API.
        # Example:
        # prompt = f"""
        # Based on the user profile: {user_profile.model_dump_json(indent=2)}
        # And the country rankings: {country_ranking.model_dump_json(indent=2)}
        # Please provide a clear, human-friendly explanation that includes:
        # 1. The user's current situation.
        # 2. Why the recommended countries ranked highest.
        # 3. Key strengths and weaknesses for the user in relation to these countries.
        # """
        # response = gemini_api.generate_text(prompt=prompt)
        # return response.text

        # For demonstration, returning a simple string
        if not country_ranking.ranked_countries:
            return "Based on your profile, there are no specific country recommendations at this time."

        top_country = country_ranking.ranked_countries[0]
        explanation = f"Hello {user_profile.personal_info.first_name}!\n\n"
        explanation += f"Based on your profile, the top recommended country for you is {top_country.country} via the {top_country.pathway} pathway.\n\n"
        explanation += f"**Your Situation:** You are a {user_profile.personal_info.age} year old {user_profile.personal_info.nationality} citizen, currently residing in {user_profile.personal_info.current_residence}. You have a {user_profile.education.degree_level} degree in {user_profile.education.field_of_study} and {user_profile.work_experience.years_of_experience} years of experience as a {user_profile.work_experience.occupation}. Your IELTS score is {user_profile.language_proficiency.ielts_score} and you have approximately ${user_profile.financial_info.liquid_assets_usd} in liquid assets.\n\n"
        explanation += f"**Why {top_country.country} ranked highest for {top_country.pathway} pathway:** This country and pathway align well with your profile due to factors such as your age, education, work experience, and financial capacity. The specific rules for {top_country.country} under the {top_country.pathway} pathway are favorable for individuals with your qualifications.\n\n"
        explanation += f"**Key Strengths:** Your {user_profile.education.degree_level} degree and {user_profile.work_experience.years_of_experience} years of experience are strong assets. Your IELTS score of {user_profile.language_proficiency.ielts_score} meets or exceeds the minimum requirements for many programs. Your liquid assets of ${user_profile.financial_info.liquid_assets_usd} also provide a good foundation.\n\n"
        explanation += f"**Key Weaknesses:** (This section would be dynamically generated based on specific rule mismatches or areas for improvement. For this placeholder, it's generic.) You might consider improving your language proficiency further or exploring additional financial planning to strengthen your application even more.\n\n"

        if len(country_ranking.ranked_countries) > 1:
            second_country = country_ranking.ranked_countries[1]
            explanation += f"The second recommended country is {second_country.country} via the {second_country.pathway} pathway. This also presents a strong option for you.\n\n"
        
        return explanation


    def _generate_fallback_explanation(self, user_profile: UserProfile, country_ranking: CountryRanking) -> str:
        if not country_ranking.ranked_countries:
            return "Based on your profile, there are no specific country recommendations at this time. Please review your input or consult with an immigration expert."

        top_country = country_ranking.ranked_countries[0]
        explanation = f"Dear {user_profile.personal_info.first_name},\n\n"
        explanation += "We have analyzed your profile and identified potential immigration pathways.\n\n"
        explanation += f"**Your Profile Summary:**\n"
        explanation += f"- Age: {user_profile.personal_info.age}\n"
        explanation += f"- Nationality: {user_profile.personal_info.nationality}\n"
        explanation += f"- Current Residence: {user_profile.personal_info.current_residence}\n"
        explanation += f"- Education: {user_profile.education.degree_level} in {user_profile.education.field_of_study}\n"
        explanation += f"- Work Experience: {user_profile.work_experience.years_of_experience} years as {user_profile.work_experience.occupation}\n"
        explanation += f"- IELTS Score: {user_profile.language_proficiency.ielts_score}\n"
        explanation += f"- Liquid Assets: ${user_profile.financial_info.liquid_assets_usd}\n\n"

        explanation += f"**Top Recommendation:** {top_country.country} - {top_country.pathway} Pathway\n"
        explanation += f"This pathway appears to be the most suitable given your current profile. The specific criteria for this pathway in {top_country.country} align well with your qualifications and resources.\n\n"
        explanation += "**Strengths:** Your educational background, work experience, and language proficiency are strong assets.\n\n"
        explanation += "**Areas for Consideration:** (This section would be dynamically generated based on specific rule mismatches or areas for improvement. For this placeholder, it's generic.) You may want to consider enhancing your financial readiness or exploring further language development.\n\n"

        if len(country_ranking.ranked_countries) > 1:
            second_country = country_ranking.ranked_countries[1]
            explanation += f"**Second Recommendation:** {second_country.country} - {second_country.pathway} Pathway\n"
            explanation += f"This is another strong option that you may wish to explore.\n\n"

        explanation += "For a more detailed analysis, please consult with an immigration specialist.\n"
        return explanation

