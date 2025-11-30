# agents/country_finder_agent.py
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root so we can import tools, agents, ...
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ============================================
# Optional logger with global toggle
# ============================================
from tools.logger import Logger, LOGGING_ENABLED as LOGGER_DEFAULT_ENABLED

LOGGER_LOCAL_ENABLED = False
LOGGING_ENABLED = LOGGER_DEFAULT_ENABLED and LOGGER_LOCAL_ENABLED



class CountryFinderAgent:
    """
    Computes final scores (0-100) for countries based on weighted factors,
    ranks them, and groups into best/acceptable/not recommended categories.
    """
    
    # Score thresholds for classification
    BEST_THRESHOLD = 80.0
    ACCEPTABLE_THRESHOLD = 60.0
    
    # Scoring weights (must sum to 1.0)
    WEIGHTS = {
        "eligibility": 0.30,           # 30% - Can you qualify?
        "language_alignment": 0.15,    # 15% - Language match
        "financial_capacity": 0.20,    # 20% - Can you afford it?
        "visa_difficulty": 0.10,       # 10% - How hard to get visa?
        "quality_of_life": 0.10,       # 10% - Safety, healthcare, etc.
        "cost_of_living": 0.10,        # 10% - Living expenses
        "job_market": 0.05,            # 5% - Employment prospects
    }
    
    # Country-specific data for scoring
    COUNTRY_DATA = {
        "Canada": {
            "visa_difficulty": 0.65,
            "quality_of_life": 0.90,
            "cost_of_living": 0.60,
            "job_market": 0.75,
            "languages": ["english", "french"],
        },
        "USA": {
            "visa_difficulty": 0.40,
            "quality_of_life": 0.85,
            "cost_of_living": 0.50,
            "job_market": 0.85,
            "languages": ["english"],
        },
        "Germany": {
            "visa_difficulty": 0.70,
            "quality_of_life": 0.90,
            "cost_of_living": 0.75,
            "job_market": 0.80,
            "languages": ["german", "english"],
        },
        "Netherlands": {
            "visa_difficulty": 0.70,
            "quality_of_life": 0.90,
            "cost_of_living": 0.65,
            "job_market": 0.75,
            "languages": ["dutch", "english"],
        },
        "Ireland": {
            "visa_difficulty": 0.65,
            "quality_of_life": 0.85,
            "cost_of_living": 0.55,
            "job_market": 0.80,
            "languages": ["english"],
        },
        "Sweden": {
            "visa_difficulty": 0.70,
            "quality_of_life": 0.95,
            "cost_of_living": 0.60,
            "job_market": 0.70,
            "languages": ["swedish", "english"],
        },
        "Australia": {
            "visa_difficulty": 0.55,
            "quality_of_life": 0.90,
            "cost_of_living": 0.50,
            "job_market": 0.80,
            "languages": ["english"],
        },
        "New Zealand": {
            "visa_difficulty": 0.65,
            "quality_of_life": 0.90,
            "cost_of_living": 0.60,
            "job_market": 0.70,
            "languages": ["english"],
        },
    }
    
    def __init__(
        self,
        match_results: List[Dict[str, Any]],
        user_profile: Dict[str, Any],
        logger: Optional["Logger"] = None,
    ):
        """
        Initialize CountryFinderAgent.
        
        Args:
            match_results: List of MatchResult dicts from MatchAgent
            user_profile: Original user profile dict
            logger: Optional shared Logger instance (shared across agents/tools)
        """
        if not match_results:
            raise ValueError("match_results cannot be empty")
        if not user_profile:
            raise ValueError("user_profile cannot be empty")
        
        self.match_results = match_results
        self.user_profile = user_profile

        # Same logger pattern as MatchAgent
        if logger is not None:
            self.logger = logger
        elif Logger and LOGGING_ENABLED:
            self.logger = Logger()
        else:
            self.logger = None

        # High-level init log
        if self.logger:
            try:
                summary = {
                    "matches_count": len(self.match_results),
                    "goal": self.user_profile.get("goal"),
                    "citizenship": self.user_profile.get("citizenship"),
                }
                self.logger.log_agent_call(
                    agent_name="CountryFinderAgent.__init__",
                    session_id=None,
                    input_summary=str(summary),
                )
            except Exception:
                pass
    
    def _score_eligibility(self, match_result: Dict[str, Any]) -> float:
        """Score eligibility based on MatchAgent result."""
        status = match_result.get("status", "High Risk")
        raw_score = match_result.get("raw_score", 0.0)
        
        if status == "OK":
            return raw_score
        elif status == "Borderline":
            return raw_score * 0.8
        else:
            return raw_score * 0.5
    
    def _score_language_alignment(self, country: str) -> float:
        """Score language alignment based on user's language skills."""
        country_data = self.COUNTRY_DATA.get(country, {})
        supported_languages = country_data.get("languages", [])
        
        score = 0.0
        
        # English
        if "english" in supported_languages:
            ielts = self.user_profile.get("ielts", 0)
            if ielts >= 7.0:
                score += 0.5
            elif ielts >= 6.0:
                score += 0.4
            elif ielts >= 5.5:
                score += 0.3
            elif ielts > 0:
                score += 0.2
        
        # German
        if "german" in supported_languages:
            german = (self.user_profile.get("german_level") or "none").lower()
            if german in ["c1", "c2"]:
                score += 0.5
            elif german in ["b1", "b2"]:
                score += 0.4
            elif german in ["a1", "a2"]:
                score += 0.2
        
        # French
        if "french" in supported_languages:
            french = (self.user_profile.get("french_level") or "none").lower()
            if french in ["c1", "c2"]:
                score += 0.5
            elif french in ["b1", "b2"]:
                score += 0.4
            elif french in ["a1", "a2"]:
                score += 0.2
        
        return min(score, 1.0)
    
    def _score_financial_capacity(self, match_result: Dict[str, Any]) -> float:
        """Score financial capacity based on funds vs requirements."""
        gaps = match_result.get("rule_gaps", {})
        missing = gaps.get("missing_requirements", [])
        
        has_funds_issue = any(
            "funds" in req.lower() or "insufficient" in req.lower()
            for req in missing
        )
        
        if not has_funds_issue:
            return 1.0
        
        raw_score = match_result.get("raw_score", 0.5)
        
        if raw_score >= 0.8:
            return 0.9
        elif raw_score >= 0.6:
            return 0.7
        elif raw_score >= 0.4:
            return 0.5
        else:
            return 0.3
    
    def _get_country_factor(self, country: str, factor: str) -> float:
        """Get a specific factor score for a country."""
        country_data = self.COUNTRY_DATA.get(country, {})
        return country_data.get(factor, 0.5)
    
    def _calculate_final_score(self, match_result: Dict[str, Any]) -> float:
        """Calculate final weighted score (0-100) for a country."""
        country = match_result.get("country", "")
        
        factors = {
            "eligibility": self._score_eligibility(match_result),
            "language_alignment": self._score_language_alignment(country),
            "financial_capacity": self._score_financial_capacity(match_result),
            "visa_difficulty": self._get_country_factor(country, "visa_difficulty"),
            "quality_of_life": self._get_country_factor(country, "quality_of_life"),
            "cost_of_living": self._get_country_factor(country, "cost_of_living"),
            "job_market": self._get_country_factor(country, "job_market"),
        }
        
        weighted_score = sum(
            self.WEIGHTS[factor] * score 
            for factor, score in factors.items()
        )
        
        final_score = weighted_score * 100
        return round(final_score, 2)
    
    def _classify_countries(self, scored_countries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Classify countries into best/acceptable/not recommended.
        """
        best_options = []
        acceptable = []
        not_recommended = []
        
        for item in scored_countries:
            country = item["country"]
            score = item["score"]
            pathway = item.get("pathway")  # ⬅️ pathway را حفظ می‌کنیم
            
            if score >= self.BEST_THRESHOLD:
                best_options.append({
                    "country": country,
                    "score": score,
                    "pathway": pathway,
                    "reason": self._generate_reason(item, "best"),
                })
            elif score >= self.ACCEPTABLE_THRESHOLD:
                acceptable.append({
                    "country": country,
                    "score": score,
                    "pathway": pathway,
                    "reason": self._generate_reason(item, "acceptable"),
                })
            else:
                # برای سازگاری، هم‌چنان فقط نام کشور را برمی‌گردانیم
                not_recommended.append(country)
        
        return {
            "best_options": best_options,
            "acceptable": acceptable,
            "not_recommended": not_recommended,
        }
    
    def _generate_reason(self, scored_item: Dict[str, Any], category: str) -> str:
        """Generate a brief reason for the score/category."""
        country = scored_item["country"]
        score = scored_item["score"]
        match_result = scored_item.get("match_result", {})
        status = match_result.get("status", "Unknown")
        
        if category == "best":
            return (
                f"Strong match with eligibility status '{status}', "
                f"good language alignment, and favorable conditions."
            )
        else:
            gaps = match_result.get("rule_gaps", {}).get("missing_requirements", [])
            if gaps:
                return (
                    f"Acceptable match but has minor gaps: {', '.join(gaps[:2])}. "
                    f"Consider addressing these to improve chances."
                )
            else:
                return f"Acceptable match with status '{status}'."
    
    def rank_countries(self) -> Dict[str, Any]:
        """
        Main method: Compute scores, rank countries, and classify them.
        """
        if self.logger:
            try:
                self.logger.log_agent_call(
                    agent_name="CountryFinderAgent.rank_countries",
                    session_id=None,
                    input_summary=f"match_results={len(self.match_results)}",
                )
            except Exception:
                pass

        scored_countries: List[Dict[str, Any]] = []
        scores_dict: Dict[str, float] = {}
        
        # Calculate score for each match result
        for match_result in self.match_results:
            country = match_result.get("country")
            if not country:
                continue
            
            final_score = self._calculate_final_score(match_result)
            pathway = match_result.get("pathway")  # ⬅️ pathway را از MatchAgent می‌گیریم
            
            scored_countries.append({
                "country": country,
                "score": final_score,
                "match_result": match_result,
                "pathway": pathway,
            })
            
            scores_dict[country] = final_score
        
        # Sort by score (descending)
        scored_countries.sort(key=lambda x: x["score"], reverse=True)
        
        # Classify into categories
        classification = self._classify_countries(scored_countries)
        
        # Build detailed breakdown for transparency
        detailed_breakdown = []
        for item in scored_countries:
            country = item["country"]
            match_result = item["match_result"]
            pathway = item.get("pathway")
            
            detailed_breakdown.append({
                "country": country,
                "pathway": pathway,
                "final_score": item["score"],
                "eligibility_status": match_result.get("status"),
                "eligibility_raw_score": match_result.get("raw_score"),
                "language_score": round(self._score_language_alignment(country) * 100, 2),
                "financial_score": round(self._score_financial_capacity(match_result) * 100, 2),
                "visa_difficulty": round(self._get_country_factor(country, "visa_difficulty") * 100, 2),
                "quality_of_life": round(self._get_country_factor(country, "quality_of_life") * 100, 2),
                "cost_of_living": round(self._get_country_factor(country, "cost_of_living") * 100, 2),
                "job_market": round(self._get_country_factor(country, "job_market") * 100, 2),
            })

        if self.logger:
            try:
                self.logger.log_tool_call(
                    "CountryFinderAgent.rank_countries.result",
                    {
                        "best_count": len(classification["best_options"]),
                        "acceptable_count": len(classification["acceptable"]),
                        "not_recommended_count": len(classification["not_recommended"]),
                    },
                )
            except Exception:
                pass
        
        return {
            "best_options": classification["best_options"],
            "acceptable": classification["acceptable"],
            "not_recommended": classification["not_recommended"],
            "scores": scores_dict,
            "detailed_breakdown": detailed_breakdown,
        }
    
    def get_top_recommendation(self) -> Optional[str]:
        """Get the single best recommended country."""
        ranking = self.rank_countries()
        
        best = ranking.get("best_options", [])
        if best:
            top_country = best[0]["country"]
            if self.logger:
                try:
                    self.logger.log_tool_call(
                        "CountryFinderAgent.get_top_recommendation",
                        {"top_country": top_country, "source": "best_options"},
                    )
                except Exception:
                    pass
            return top_country
        
        acceptable = ranking.get("acceptable", [])
        if acceptable:
            top_country = acceptable[0]["country"]
            if self.logger:
                try:
                    self.logger.log_tool_call(
                        "CountryFinderAgent.get_top_recommendation",
                        {"top_country": top_country, "source": "acceptable"},
                    )
                except Exception:
                    pass
            return top_country
        
        if self.logger:
            try:
                self.logger.log_tool_call(
                    "CountryFinderAgent.get_top_recommendation",
                    {"top_country": None, "source": "none"},
                )
            except Exception:
                pass
        
        return None
