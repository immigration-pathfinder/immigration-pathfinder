# agents/explain_agent.py

import json
from typing import Optional
import sys
from pathlib import Path
import os

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Imports
from memory.session_service import SessionService
from tools.search_tool import SearchTool
from tools.currency_converter import CurrencyConverter
from tools.funds_gap_calculator import FundsGapCalculator
from schemas.user_profile import UserProfile
from schemas.country_ranking import CountryRanking

# Logger
from tools.logger import Logger, LOGGING_ENABLED as LOGGER_DEFAULT_ENABLED

# Logging toggle
LOGGER_LOCAL_ENABLED = False
LOGGING_ENABLED = LOGGER_DEFAULT_ENABLED and LOGGER_LOCAL_ENABLED

# Gemini (optional)
try:
    import google.generativeai as genai
except Exception:
    genai = None


class ExplainAgent:
    def __init__(
        self,
        session_service: Optional[SessionService],
        search_tool: Optional[SearchTool],
        logger: Optional["Logger"] = None,
        funds_calculator: Optional[FundsGapCalculator] = None,
        currency_converter: Optional[CurrencyConverter] = None,
    ):
        self.session_service = session_service
        self.search_tool = search_tool
        self.funds_calculator = funds_calculator
        self.currency_converter = currency_converter

        # Logger setup
        if logger is not None:
            self.logger = logger
        elif Logger and LOGGING_ENABLED:
            self.logger = Logger()
        else:
            self.logger = None

        # Gemini setup
        self.gemini_enabled = False
        self.gemini_model = None

        api_key = os.getenv("GEMINI_API_KEY")

        if api_key and genai is not None:
            try:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel("gemini-1.5-pro")
                self.gemini_enabled = True
                print("✅ Gemini API connected successfully!")
            except Exception as e:
                self.gemini_enabled = False
                print(f"⚠️  Gemini setup failed: {e}")
                print("📝 Running in offline mode (using fallback templates)")
                if self.logger:
                    self.logger.log_exception(e, "ExplainAgent Gemini setup failed")

        if self.logger:
            self.logger.log_agent_call(
                "ExplainAgent.__init__",
                None,
                f"GeminiEnabled={self.gemini_enabled}",
            )

    def generate_explanation(
        self,
        user_profile: UserProfile,
        country_ranking: CountryRanking,
    ) -> str:
        """Generate immigration explanation (Gemini or fallback)"""

        if self.logger:
            try:
                self.logger.log_agent_call(
                    "ExplainAgent.generate_explanation",
                    None,
                    f"user={getattr(user_profile.personal_info, 'first_name', 'N/A')}, "
                    f"ranked={len(country_ranking.ranked_countries or [])}",
                )
            except Exception:
                pass

        # Try Gemini first
        if self.gemini_enabled:
            try:
                print("🤖 Generating explanation with Gemini AI...")
                output = self._generate_with_gemini(user_profile, country_ranking)
                if self.logger:
                    self.logger.log_tool_call(
                        "ExplainAgent.generate_explanation",
                        {"mode": "gemini", "chars": len(output)},
                    )
                return output
            except Exception as e:
                if self.logger:
                    self.logger.log_exception(e, "Gemini generation failed")
                print(f"⚠️  Gemini API failed: {e}")
                print("📝 Switching to offline mode...")
        else:
            # اگر از اول Gemini خاموش بود
            print("📝 Generating explanation in offline mode (no AI)...")

        # Fallback mode
        output = self._generate_fallback(user_profile, country_ranking)
        if self.logger:
            try:
                self.logger.log_tool_call(
                    "ExplainAgent.generate_explanation",
                    {"mode": "offline", "chars": len(output)},
                )
            except Exception:
                pass
        return output

    def _generate_with_gemini(
        self,
        user_profile: UserProfile,
        ranking: CountryRanking,
    ) -> str:
        """Generate explanation using Gemini AI with enhanced search"""

        if not ranking.ranked_countries:
            return "❌ No recommended countries found for your profile."

        top = ranking.ranked_countries[0]

        # ✅ استفاده از SearchTool برای اطلاعات تازه
        search_context = ""
        if self.search_tool:
            print(f"   🔍 Searching for latest {top.country} visa information...")
            try:
                search_results = self.search_tool.search_immigration(
                    query="visa requirements",
                    country=top.country,
                    pathway=top.pathway or "Work",
                    max_results=3,
                )

                if search_results:
                    search_context = "\n\nLATEST INFORMATION FROM WEB:\n"
                    for i, result in enumerate(search_results[:2], 1):
                        search_context += (
                            f"{i}. {result['title']}\n   {result['snippet']}\n"
                        )
            except Exception as e:
                print(f"   ⚠️  Search failed: {e}")

        prompt = f"""
You are an expert immigration advisor. Provide a clear, friendly recommendation.

USER PROFILE:
{user_profile.model_dump_json(indent=2)}

COUNTRY RANKING:
{ranking.model_dump_json(indent=2)}

{search_context}

TASK:
1. Explain why "{top.country}" is the best match
2. Summarize the user's key qualifications
3. List 2-3 strengths
4. List 1-2 areas for improvement
5. Suggest next steps
6. If available, incorporate the latest visa information from web search

Keep it concise, professional, and encouraging.
"""

        result = self.gemini_model.generate_content(prompt)
        text = getattr(result, "text", None) or str(result)
        return text.strip()

    def _generate_fallback(
        self,
        user_profile: UserProfile,
        ranking: CountryRanking,
    ) -> str:
        """Generate explanation without AI (offline mode)"""

        if not ranking.ranked_countries:
            return (
                "❌ No country recommendations available.\n\n"
                "This could be due to:\n"
                "• Incomplete profile information\n"
                "• No matching pathways found\n\n"
                "💡 Tip: Try updating your profile or consult an immigration expert."
            )

        top = ranking.ranked_countries[0]
        personal = user_profile.personal_info
        edu = user_profile.education
        work = user_profile.work_experience
        lang = user_profile.language_proficiency
        finance = user_profile.financial_info

        # ✅  SearchTool 
        search_info = ""
        if self.search_tool:
            try:
                results = self.search_tool.search_immigration(
                    query="visa requirements",
                    country=top.country,
                    pathway=top.pathway or "Work",
                    max_results=2,
                )
                if results and results[0].get("snippet"):
                    search_info = (
                        f"\n💡 **Latest Info:** {results[0]['snippet'][:200]}...\n"
                    )
            except Exception:
                pass

        # 🔍 تحلیل مالی (اختیاری) با FundsGapCalculator و CurrencyConverter
        funds_analysis_text = ""
        if (
            self.funds_calculator
            and finance is not None
            and getattr(finance, "liquid_assets_usd", None) is not None
        ):
            try:
                pathway = top.pathway or "Study"

                needs = self.funds_calculator.calculate_total_needs(
                    country=top.country,
                    pathway=pathway,
                    duration_months=12,
                    include_tuition=True,
                )

                gap = self.funds_calculator.calculate_gap(
                    available=float(finance.liquid_assets_usd or 0.0),
                    required=float(needs["total_needed"]),
                    currency="USD",
                )

                funds_analysis_text += (
                    f"\n💰 **Financial Overview for {top.country} ({pathway}):**\n"
                    f"   • Estimated total funds needed: ${needs['total_needed']:,.0f} USD\n"
                    f"   • Your available funds: ${finance.liquid_assets_usd:,.0f} USD\n"
                    f"   • Coverage: {gap['coverage_percent']}% ({gap['status']})\n"
                    f"   • Tip: {gap['suggestion']}\n"
                )

                # تبدیل نمونه‌ای به EUR (اگر CurrencyConverter موجود باشد)
                if self.currency_converter:
                    try:
                        approx_eur = self.currency_converter.convert(
                            amount=float(finance.liquid_assets_usd or 0.0),
                            from_curr="USD",
                            to_curr="EUR",
                            decimals=0,
                        )
                        funds_analysis_text += (
                            f"   • In EUR this is approximately: €{approx_eur:,.0f}\n"
                        )
                    except Exception:
                        pass

            except Exception:
                
                pass

        # Build explanation
        explanation = f"🌍 **Immigration Recommendation for {personal.first_name}**\n\n"
        explanation += "═══════════════════════════════════════\n\n"

        # Top recommendation
        explanation += f"🥇 **Top Choice: {top.country}**\n"
        explanation += f"   Pathway: {top.pathway or 'Work/Study'}\n"
        explanation += f"   Match Score: {getattr(top, 'score', 'N/A')}\n"

        # ✅ ا
        if search_info:
            explanation += search_info

        explanation += "\n"

        # Profile summary
        explanation += "📋 **Your Profile:**\n"
        explanation += f"   • Age: {personal.age} years\n"
        explanation += f"   • Nationality: {personal.nationality}\n"
        explanation += f"   • Education: {edu.degree_level} in {edu.field_of_study}\n"
        explanation += (
            f"   • Experience: {work.years_of_experience} years as {work.occupation}\n"
        )
        explanation += (
            f"   • English: IELTS {lang.ielts_score if lang.ielts_score else 'Not provided'}\n"
        )
        explanation += (
            f"   • Funds: ${finance.liquid_assets_usd:,.2f} USD\n"
            if finance and finance.liquid_assets_usd is not None
            else "   • Funds: Not provided\n"
        )

        # 🔹 اگر تحلیل مالی داشتیم، اینجا اضافه کن
        if funds_analysis_text:
            explanation += funds_analysis_text + "\n"

        explanation += "\n"

        # Strengths
        explanation += "✅ **Your Strengths:**\n"
        strengths = []

        if edu.degree_level in ["bachelor", "master", "phd"]:
            strengths.append(
                f"   • Strong educational background ({edu.degree_level})"
            )

        if work.years_of_experience >= 2:
            strengths.append(
                f"   • Valuable work experience ({work.years_of_experience} years)"
            )

        if finance and finance.liquid_assets_usd is not None:
            if finance.liquid_assets_usd >= 10000:
                strengths.append(
                    f"   • Solid financial foundation (${finance.liquid_assets_usd:,.0f})"
                )

        if lang.ielts_score and lang.ielts_score >= 6.5:
            strengths.append(
                f"   • Good English proficiency (IELTS {lang.ielts_score})"
            )

        if not strengths:
            strengths.append("   • Eligible for multiple immigration pathways")

        explanation += "\n".join(strengths) + "\n\n"

        # Areas for improvement
        explanation += "💡 **Consider Improving:**\n"
        improvements = []

        if not lang.ielts_score or lang.ielts_score < 6.5:
            improvements.append("   • Take IELTS test to improve language score")

        if not finance or finance.liquid_assets_usd is None:
            improvements.append(
                "   • Provide clear information about your available funds"
            )
        elif finance.liquid_assets_usd < 15000:
            improvements.append("   • Build more savings for settlement funds")

        if work.years_of_experience < 3:
            improvements.append(
                "   • Gain more work experience in your field to strengthen your profile"
            )

        if improvements:
            explanation += "\n".join(improvements) + "\n\n"
        else:
            explanation += (
                "   • Your profile is strong! Focus on preparing a clean application.\n\n"
            )

        # Second recommendation
        if len(ranking.ranked_countries) > 1:
            second = ranking.ranked_countries[1]
            explanation += f"🥈 **Alternative: {second.country}**\n"
            explanation += (
                f"   Pathway: {second.pathway or 'Work/Study'}\n\n"
            )

        # Next steps
        explanation += "🎯 **Next Steps:**\n"
        explanation += "   1. Research visa requirements for your top choice\n"
        explanation += "   2. Prepare necessary documents (diplomas, work letters)\n"
        explanation += "   3. Take/improve IELTS if needed\n"
        explanation += (
            "   4. Consult with a licensed immigration consultant if possible\n\n"
        )

        explanation += "═══════════════════════════════════════\n"
        explanation += "💬 Good luck with your immigration journey!\n"

        return explanation
