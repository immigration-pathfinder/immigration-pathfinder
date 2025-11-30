# agents/explain_agent.py

import json
from typing import Optional
import sys
from pathlib import Path
import os

# ----------------------------------------------------
# Project root for imports
# ----------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ----------------------------------------------------
# Imports
# ----------------------------------------------------
from memory.session_service import SessionService
from tools.search_tool import SearchTool
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
    """
    ExplainAgent

    مسئولیت:
      - گرفتن UserProfile و CountryRanking
      - تولید یک توضیح انسانی (با Gemini اگر فعال بود، وگرنه حالت آفلاین)
      - در صورت نبودن هیچ کشور ریکامند شده، توضیح شفاف "چرا هیچ پیشنهادی نیست"
    """

    def __init__(
        self,
        session_service: Optional[SessionService],
        search_tool: Optional[SearchTool],
        logger: Optional["Logger"] = None,
    ):
        self.session_service = session_service
        self.search_tool = search_tool

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
                self.gemini_model = genai.GenerativeModel("gemini-pro")
                self.gemini_enabled = True
                print("✅ Gemini API connected successfully! (model: gemini-pro)")
            except Exception as e:
                self.gemini_enabled = False
                print(f"⚠️  Gemini setup failed: {e}")
                print("📝 Running in offline mode (using fallback templates)")
                if self.logger:
                    self.logger.log_exception(e, "ExplainAgent Gemini setup failed")
        else:
            self.gemini_enabled = False
            if not api_key:
                print("ℹ️  No GEMINI_API_KEY found - running in offline mode")
            elif genai is None:
                print("ℹ️  google-generativeai not installed - running in offline mode")

        if self.logger:
            self.logger.log_agent_call(
                "ExplainAgent.__init__",
                None,
                f"GeminiEnabled={self.gemini_enabled}",
            )

    # ------------------------------------------------
    # Public entrypoint
    # ------------------------------------------------
    def generate_explanation(
        self,
        user_profile: UserProfile,
        country_ranking: CountryRanking,
    ) -> str:
        """Generate immigration explanation (Gemini or offline)"""

        if self.logger:
            self.logger.log_agent_call(
                "ExplainAgent.generate_explanation",
                None,
                f"user={user_profile.personal_info.first_name}, "
                f"ranked={len(country_ranking.ranked_countries or [])}",
            )

        # ✅ اگر هیچ کشوری ریکامند نشده، مستقیم یک توضیح اختصاصی بساز
        if not country_ranking.ranked_countries:
            output = self._generate_no_recommendation_explanation(
                user_profile,
                country_ranking,
            )
            if self.logger:
                self.logger.log_tool_call(
                    "ExplainAgent.generate_explanation",
                    {
                        "mode": "no_recommendation_offline",
                        "chars": len(output),
                    },
                )
            return output

        # از اینجا به بعد: حداقل یک کشور داریم → می‌تونیم Gemini یا fallback عادی را استفاده کنیم

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
            print("📝 Generating explanation in offline mode (no AI)...")

        # Fallback mode (بدون Gemini)
        output = self._generate_fallback(user_profile, country_ranking)
        if self.logger:
            self.logger.log_tool_call(
                "ExplainAgent.generate_explanation",
                {"mode": "offline", "chars": len(output)},
            )
        return output

    # ------------------------------------------------
    # Gemini mode
    # ------------------------------------------------
    def _generate_with_gemini(
        self,
        user_profile: UserProfile,
        ranking: CountryRanking,
    ) -> str:
        """Generate explanation using Gemini AI with enhanced search"""

        if not ranking.ranked_countries:
            # این حالت را در generate_explanation هندل کردیم،
            # اما برای اطمینان یک پیام ساده نگه می‌داریم
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
                        title = result.get("title", "")
                        snippet = result.get("snippet", "")
                        search_context += f"{i}. {title}\n   {snippet}\n"
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
1. Explain why "{top.country}" is the best match.
2. Summarize the user's key qualifications.
3. List 2-3 strengths.
4. List 1-2 areas for improvement.
5. Suggest next steps.
6. If available, incorporate the latest visa information from web search.

Keep it concise, professional, and encouraging.
Format in Markdown.
"""

        result = self.gemini_model.generate_content(prompt)

        # ✅ پردازش response به شکل امن
        text = None
        if hasattr(result, "text"):
            text = result.text
        elif hasattr(result, "candidates") and result.candidates:
            try:
                parts = result.candidates[0].content.parts
                text = "".join(p.text for p in parts if hasattr(p, "text"))
            except Exception:
                pass

        if not text:
            text = str(result)

        return text.strip()

    # ------------------------------------------------
    # Case: no recommended countries
    # ------------------------------------------------
    def _generate_no_recommendation_explanation(
        self,
        user_profile: UserProfile,
        ranking: CountryRanking,
    ) -> str:
        """
        وقتی هیچ کشوری در ranked_countries نیست، این متد توضیح می‌دهد
        که چرا هیچ پیشنهادی وجود ندارد (با تأکید روی پول، هدف، و پروفایل).
        """

        personal = user_profile.personal_info
        edu = user_profile.education
        work = user_profile.work_experience
        lang = user_profile.language_proficiency
        finance = user_profile.financial_info

        funds = float(finance.liquid_assets_usd or 0.0)
        goal_raw = (user_profile.immigration_goal or "").strip().lower()

        # ✅ حداقل پول بر اساس هدف
        if goal_raw == "study":
            hard_limit = 11000.0   # تقریبی بر اساس rules فعلی برای استادی
            goal_label = "Study"
        elif goal_raw == "pr":
            hard_limit = 8000.0
            goal_label = "Permanent Residence (PR)"
        else:
            # Work یا چیز دیگر
            hard_limit = 4000.0
            goal_label = "Work"

        # 🔥 اگر پول زیر حد این هدف است → دلیل اصلی = پول
        if funds < hard_limit:
            return (
                "❌ **No recommended countries found for your profile.**\n\n"
                "### Main Reason: Insufficient Funds for Your Goal\n"
                f"- Your available funds: **${funds:,.0f} USD**\n"
                f"- Minimum realistic funds for **{goal_label}** pathways: "
                f"**around ${hard_limit:,.0f} USD or more** (for a single applicant)\n\n"
                "Most study/work/PR visas require you to prove you can pay your living "
                "costs for at least one year (and sometimes tuition as well). With your "
                "current savings, your application would be **very high risk** in almost "
                "all target countries.\n\n"
                "### What You Can Do:\n"
                "1. Increase your savings (ideally above this minimum level).\n"
                "2. Consider cheaper destinations or work-based routes instead of study.\n"
                "3. Look for scholarships or fully-funded programs to reduce required funds.\n\n"
                "💡 When your funds increase, re-run the Immigration Pathfinder for new recommendations."
            )

        # ✅ اگر مشکل اصلی پول نبوده، یک پیام عمومی‌تر (سن/زبان/قوانین)
        return (
            "❌ **No recommended countries found for your profile.**\n\n"
            "This usually happens when:\n"
            "- Your current profile (age, degree, English, funds) does not reach the minimum thresholds, or\n"
            "- All options are classified as **high risk** for visa approval.\n\n"
            "### Quick Summary of Your Profile:\n"
            f"- Age: **{personal.age}**\n"
            f"- Education: **{edu.degree_level} in {edu.field_of_study or 'N/A'}**\n"
            f"- Work Experience: **{work.years_of_experience} years**\n"
            f"- IELTS: **{lang.ielts_score or 0}**\n"
            f"- Available Funds: **${funds:,.0f} USD**\n\n"
            "### Suggestions:\n"
            "- Improve your English score (IELTS 6.0–6.5+ for most Study/Work paths).\n"
            "- Increase your savings if possible.\n"
            "- Consider adjusting your goal (e.g., Work instead of Study) or your target countries.\n"
        )

    # ------------------------------------------------
    # Offline fallback when there *are* recommendations
    # ------------------------------------------------
    def _generate_fallback(
        self,
        user_profile: UserProfile,
        ranking: CountryRanking,
    ) -> str:
        """Generate explanation without AI (offline mode)"""

        if not ranking.ranked_countries:
            # از لحاظ منطقی، اینجا نباید بیایم (در generate_explanation هندل شده)
            # ولی برای احتیاط، از همان no_recommendation استفاده می‌کنیم.
            return self._generate_no_recommendation_explanation(user_profile, ranking)

        top = ranking.ranked_countries[0]
        personal = user_profile.personal_info
        edu = user_profile.education
        work = user_profile.work_experience
        lang = user_profile.language_proficiency
        finance = user_profile.financial_info

        # تلاش برای افزودن یک snippet از SearchTool (در حالت آفلاین هم ممکن است mock برگرداند)
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
                    snippet = results[0]["snippet"][:200]
                    search_info = f"\n💡 **Latest Info:** {snippet}...\n"
            except Exception:
                pass  # اگر سرچ خراب شد، توضیح اصلی را ادامه می‌دهیم

        explanation = f"🌍 **Immigration Recommendation for {personal.first_name}**\n\n"
        explanation += "═══════════════════════════════════════\n\n"

        # Top recommendation
        explanation += f"🥇 **Top Choice: {top.country}**\n"
        explanation += f"   Pathway: {top.pathway or 'Work/Study'}\n"
        explanation += f"   Match Score: {getattr(top, 'score', 'N/A')}\n"

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
        explanation += f"   • Funds: ${finance.liquid_assets_usd:,.2f} USD\n\n"

        # Strengths
        explanation += "✅ **Your Strengths:**\n"
        strengths = []

        if edu.degree_level in ["bachelor", "master", "phd"]:
            strengths.append(f"   • Strong educational background ({edu.degree_level})")

        if work.years_of_experience >= 2:
            strengths.append(
                f"   • Valuable work experience ({work.years_of_experience} years)"
            )

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
            improvements.append("   • Take IELTS test to improve your language score")

        if finance.liquid_assets_usd < 15000:
            improvements.append("   • Build more savings for settlement funds")

        if work.years_of_experience < 3:
            improvements.append("   • Gain more work experience in your field")

        if improvements:
            explanation += "\n".join(improvements) + "\n\n"
        else:
            explanation += "   • Your profile is strong! Focus on the application process.\n\n"

        # Second recommendation (optional)
        if len(ranking.ranked_countries) > 1:
            second = ranking.ranked_countries[1]
            explanation += f"🥈 **Alternative: {second.country}**\n"
            explanation += f"   Pathway: {second.pathway or 'Work/Study'}\n\n"

        # Next steps
        explanation += "🎯 **Next Steps:**\n"
        explanation += "   1. Research visa requirements for your top choice.\n"
        explanation += "   2. Prepare necessary documents (diplomas, work letters).\n"
        explanation += "   3. Take/improve IELTS if needed.\n"
        explanation += "   4. Consider consulting with a licensed immigration consultant.\n\n"

        explanation += "═══════════════════════════════════════\n"
        explanation += "💬 Good luck with your immigration journey!\n"

        return explanation
