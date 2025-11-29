import sys
from pathlib import Path
from typing import Any, Dict, Optional
import json

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.logger import Logger, LOGGING_ENABLED as LOGGER_DEFAULT_ENABLED

# toggle
LOGGER_LOCAL_ENABLED = False
LOGGING_ENABLED = LOGGER_DEFAULT_ENABLED and LOGGER_LOCAL_ENABLED

from agents.profile_agent import ProfileAgent
from agents.match_agent import MatchAgent
from agents.country_finder_agent import CountryFinderAgent
from agents.explain_agent import ExplainAgent

# ✅ tools
from tools.search_tool import SearchTool
from tools.currency_converter import CurrencyConverter
from tools.funds_gap_calculator import FundsGapCalculator  

# models
from schemas.user_profile import (
    UserProfile,
    PersonalInfo,
    Education,
    WorkExperience,
    LanguageProficiency,
    FinancialInfo,
)
from schemas.country_ranking import RankedCountry, CountryRanking


class Orchestrator:
    """
    Orchestrator: Main coordinator of the Multi-Agent System
    
    Responsibilities:
    -----------------
    1. Receive user information (as dict or raw text)
    2. Coordinate all agents:
       - ProfileAgent: Extract user profile
       - MatchAgent: Evaluate eligibility
       - CountryFinderAgent: Rank countries
       - ExplainAgent: Generate explanations
    3. Return the final structured output
    """

    
    def __init__(self, session_service=None, logger: Optional[Logger] = None) -> None:
        """
        Initialize Orchestrator with all agents and tools
        
        Args:
            session_service: Optional session service (for compatibility)
            logger: Optional logger instance
        """
        
        # logger
        if logger is not None:
            self.logger = logger
        elif Logger and LOGGING_ENABLED:
            self.logger = Logger()
        else:
            self.logger = None

        # ✅ Initialize tools
        print("🔧 Initializing tools...")
        self.search_tool = SearchTool()
        self.currency_converter = CurrencyConverter()
        self.funds_calculator = FundsGapCalculator()

        # rules
        rules_path = PROJECT_ROOT / "rules" / "country_rules.json"
        with open(rules_path, "r", encoding="utf-8") as f:
            country_rules = json.load(f)

        # agents
        print("🤖 Initializing agents...")
        self.profile_agent = ProfileAgent(logger=self.logger)
        self.match_agent = MatchAgent(rules=country_rules, logger=self.logger)
        
        # ✅ ExplainAgent با tools
        self.explain_agent = ExplainAgent(
            session_service=session_service,
            search_tool=self.search_tool,
            logger=self.logger,
            funds_calculator=self.funds_calculator,
            currency_converter=self.currency_converter,
        )

        if self.logger:
            self.logger.log_agent_call(
                "Orchestrator.__init__",
                None,
                f"Loaded rules: {len(country_rules)}, Tools: 3",
            )
        
        print("✅ Orchestrator initialized with all agents and tools!")

    def _convert_profile_to_model(self, profile: Dict[str, Any]) -> UserProfile:
        """
        تبدیل dict به Pydantic UserProfile model

        این متد مطمئن می‌شود که اگر ProfileAgent بعضی فیلدها را خالی گذاشت (None)،
        مقدارهای پیش‌فرض امن برای Pydantic ارسال شود.
        """

        # Safe defaults for missing values
        age = profile.get("age")
        if age is None:
            age = 0  # fallback, required int

        citizenship = profile.get("citizenship")
        if citizenship is None:
            citizenship = "Unknown"

        current_residence = profile.get("citizenship")
        if current_residence is None:
            current_residence = "Unknown"

        return UserProfile(
            personal_info=PersonalInfo(
                first_name="User",
                last_name="",
                age=age,
                nationality=citizenship,
                current_residence=current_residence,
                marital_status=profile.get("marital_status") or "unknown",
            ),
            education=Education(
                degree_level=profile.get("education_level") or "",
                field_of_study=profile.get("field_of_study") or "",
            ),
            work_experience=WorkExperience(
                years_of_experience=profile.get("work_experience_years") or 0,
                occupation=profile.get("field_of_study") or "Unknown",
            ),
            language_proficiency=LanguageProficiency(
                ielts_score=profile.get("english_score") or 0,
                cefr_level=profile.get("english_level") or "A1",
            ),
            financial_info=FinancialInfo(
                liquid_assets_usd=profile.get("funds_usd") or 0,
            ),
            immigration_goal=profile.get("goal") or "work",
            preferred_countries=profile.get("target_countries") or [],
            goals=[profile.get("goal") or ""],
            target_countries=profile.get("target_countries") or [],
        )


    def _convert_ranking_to_model(self, ranking: Dict[str, Any]) -> CountryRanking:
        """
         dict Pydantic CountryRanking model
        """

        ranked: list[RankedCountry] = []

        for item in ranking.get("best_options", []):
            ranked.append(
                RankedCountry(
                    country=item["country"],
                    pathway=item.get("pathway", "Unknown"),
                    score=item["score"],
                )
            )

        for item in ranking.get("acceptable", []):
            ranked.append(
                RankedCountry(
                    country=item["country"],
                    pathway=item.get("pathway", "Unknown"),
                    score=item["score"],
                )
            )

        return CountryRanking(ranked_countries=ranked)

    def process(self, user_profile: Dict[str, Any], query: str = "") -> Dict[str, Any]:
        """
        🎯 متد اصلی: پردازش کامل درخواست کاربر
        """

        if self.logger:
            self.logger.log_agent_call(
                "Orchestrator.process",
                None,
                f"query={query[:100] if query else 'none'}",
            )

        # Build raw text for ProfileAgent
        raw_text = self._build_raw_text_from_dict(user_profile, query)

        # ========================================
        # Step 1: Extract user profile
        # ========================================
        print("🔍 Step 1/4: Extracting profile information...")
        profile = self.profile_agent.run(raw_text)

        # ========================================
        # Step 2: Evaluate country eligibility
        # ========================================
        print("⚖️  Step 2/4: Evaluating country eligibility...")
        match_results = self.match_agent.evaluate_all(profile)

        # ========================================
        # Step 3: Rank countries
        # ========================================
        print("📊 Step 3/4: Ranking countries...")
        cf = CountryFinderAgent(
            match_results=match_results,
            user_profile=profile,
            logger=self.logger,
        )
        ranking = cf.rank_countries()
        recommended = cf.get_top_recommendation()

        # ========================================
        # Step 4: Generate explanation
        # ========================================
        print("📝 Step 4/4: Generating explanation...")
        profile_model = self._convert_profile_to_model(profile)
        ranking_model = self._convert_ranking_to_model(ranking)
        explanation = self.explain_agent.generate_explanation(
            profile_model,
            ranking_model,
        )
        
        print("✅ Processing complete!\n")

        return {
            "profile": profile,
            "match_results": match_results,
            "ranking": ranking,
            "recommended_country": recommended,
            "explanation": explanation,
        }

    def run(self, raw_text: str) -> Dict[str, Any]:
        """
        🔄 raw text
        """

        if self.logger:
            self.logger.log_agent_call(
                "Orchestrator.run",
                None,
                raw_text[:200],
            )

        print("🔍 Step 1/4: Extracting profile information...")
        profile = self.profile_agent.run(raw_text)

        print("⚖️  Step 2/4: Evaluating country eligibility...")
        match_results = self.match_agent.evaluate_all(profile)

        print("📊 Step 3/4: Ranking countries...")
        cf = CountryFinderAgent(
            match_results=match_results,
            user_profile=profile,
            logger=self.logger,
        )
        ranking = cf.rank_countries()
        recommended = cf.get_top_recommendation()

        print("📝 Step 4/4: Generating explanation...")
        profile_model = self._convert_profile_to_model(profile)
        ranking_model = self._convert_ranking_to_model(ranking)
        explanation = self.explain_agent.generate_explanation(
            profile_model,
            ranking_model,
        )
        
        print("✅ Processing complete!\n")

        return {
            "profile": profile,
            "match_results": match_results,
            "ranking": ranking,
            "recommended_country": recommended,
            "explanation": explanation,
        }

    def _build_raw_text_from_dict(self, user_profile: Dict[str, Any], query: str = "") -> str:
        """
        🔧 Helper: تبدیل dict به raw text برای ProfileAgent
        """
        
        parts = []
        
        if user_profile.get("age"):
            parts.append(f"I am {user_profile['age']} years old")
        
        if user_profile.get("citizenship"):
            parts.append(f"from {user_profile['citizenship']}")
        
        if user_profile.get("marital_status"):
            parts.append(f"I am {user_profile['marital_status']}")
        
        if user_profile.get("education_level"):
            parts.append(f"I have a {user_profile['education_level']} degree")
        
        if user_profile.get("field_of_study"):
            parts.append(f"in {user_profile['field_of_study']}")
        
        if user_profile.get("work_experience_years"):
            parts.append(f"I have {user_profile['work_experience_years']} years of work experience")
        
        if user_profile.get("english_level"):
            parts.append(f"My English level is {user_profile['english_level']}")
        
        if user_profile.get("english_score"):
            parts.append(f"IELTS score: {user_profile['english_score']}")
        
        if user_profile.get("funds_usd"):
            parts.append(f"I have {user_profile['funds_usd']} USD in savings")
        
        if user_profile.get("goal"):
            parts.append(f"My goal is {user_profile['goal']}")
        
        if user_profile.get("target_countries"):
            countries = ", ".join(user_profile["target_countries"])
            parts.append(f"My target countries are {countries}")
        
        if query:
            parts.append(f"\nQuery: {query}")
        
        return ". ".join(parts) + "."


if __name__ == "__main__":
    # Test with raw text
    text = """
    I am 30 years old and from Iran.
    I have a bachelor degree in computer engineering.
    I have 2 years of work experience.
    My English level is B1.
    I have 10000 USD savings.
    My goal is work.
    My target countries are Germany and Netherlands.
    """

    print("="*60)
    print("Testing Orchestrator with raw text")
    print("="*60)
    
    orch = Orchestrator()
    out = orch.run(text)
    
    # Print explanation nicely
    if "explanation" in out:
        print("\n📄 RECOMMENDATION:\n")
        print(out["explanation"])
        print("\n" + "="*60)
    
    # Print technical details
    print("\n📊 TECHNICAL DETAILS:")
    out_copy = out.copy()
    out_copy.pop("explanation", None)
    print(json.dumps(out_copy, indent=2, ensure_ascii=False))
