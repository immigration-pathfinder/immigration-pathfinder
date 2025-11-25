# agents/country_finder_agent.py
from typing import List, Dict, Any, Optional


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
        "language_alignment": 0.15,     # 15% - Language match
        "financial_capacity": 0.20,     # 20% - Can you afford it?
        "visa_difficulty": 0.10,        # 10% - How hard to get visa?
        "quality_of_life": 0.10,        # 10% - Safety, healthcare, etc.
        "cost_of_living": 0.10,         # 10% - Living expenses
        "job_market": 0.05,             # 5% - Employment prospects
    }
    
    # Country-specific data for scoring
    COUNTRY_DATA = {
        "Canada": {
            "visa_difficulty": 0.65,      # Moderate (0=hardest, 1=easiest)
            "quality_of_life": 0.90,      # Very high
            "cost_of_living": 0.60,       # Moderate-high (0=expensive, 1=cheap)
            "job_market": 0.75,           # Good opportunities
            "languages": ["english", "french"],
        },
        "USA": {
            "visa_difficulty": 0.40,      # Difficult
            "quality_of_life": 0.85,      # High
            "cost_of_living": 0.50,       # Expensive
            "job_market": 0.85,           # Excellent
            "languages": ["english"],
        },
        "Germany": {
            "visa_difficulty": 0.70,      # Relatively easier
            "quality_of_life": 0.90,      # Very high
            "cost_of_living": 0.75,       # Moderate (free tuition!)
            "job_market": 0.80,           # Strong
            "languages": ["german", "english"],
        },
        "Netherlands": {
            "visa_difficulty": 0.70,      # Relatively easier
            "quality_of_life": 0.90,      # Very high
            "cost_of_living": 0.65,       # Moderate
            "job_market": 0.75,           # Good
            "languages": ["dutch", "english"],
        },
        "Ireland": {
            "visa_difficulty": 0.65,      # Moderate
            "quality_of_life": 0.85,      # High
            "cost_of_living": 0.55,       # Expensive
            "job_market": 0.80,           # Strong (tech hub)
            "languages": ["english"],
        },
        "Sweden": {
            "visa_difficulty": 0.70,      # Relatively easier
            "quality_of_life": 0.95,      # Excellent
            "cost_of_living": 0.60,       # Moderate-high
            "job_market": 0.70,           # Good
            "languages": ["swedish", "english"],
        },
        "Australia": {
            "visa_difficulty": 0.55,      # Moderate-difficult
            "quality_of_life": 0.90,      # Very high
            "cost_of_living": 0.50,       # Expensive
            "job_market": 0.80,           # Strong
            "languages": ["english"],
        },
        "New Zealand": {
            "visa_difficulty": 0.65,      # Moderate
            "quality_of_life": 0.90,      # Very high
            "cost_of_living": 0.60,       # Moderate
            "job_market": 0.70,           # Good
            "languages": ["english"],
        },
    }
    
    def __init__(self, match_results: List[Dict[str, Any]], user_profile: Dict[str, Any]):
        """
        Initialize CountryFinderAgent.
        
        Args:
            match_results: List of MatchResult dicts from MatchAgent
            user_profile: Original user profile dict
        """
        if not match_results:
            raise ValueError("match_results cannot be empty")
        if not user_profile:
            raise ValueError("user_profile cannot be empty")
        
        self.match_results = match_results
        self.user_profile = user_profile
    
    def _score_eligibility(self, match_result: Dict[str, Any]) -> float:
        """
        Score eligibility based on MatchAgent result.
        
        Args:
            match_result: Single MatchResult dict
            
        Returns:
            Score 0.0-1.0
        """
        status = match_result.get("status", "High Risk")
        raw_score = match_result.get("raw_score", 0.0)
        
        # Status-based adjustment
        if status == "OK":
            return raw_score  # Use raw score directly
        elif status == "Borderline":
            return raw_score * 0.8  # Slight penalty
        else:  # High Risk
            return raw_score * 0.5  # Heavy penalty
    
    def _score_language_alignment(self, country: str) -> float:
        """
        Score language alignment based on user's language skills.
        
        Args:
            country: Country name
            
        Returns:
            Score 0.0-1.0
        """
        country_data = self.COUNTRY_DATA.get(country, {})
        supported_languages = country_data.get("languages", [])
        
        score = 0.0
        
        # Check English proficiency (IELTS)
        if "english" in supported_languages:
            ielts = self.user_profile.get("ielts", 0)
            if ielts >= 7.0:
                score += 0.5  # Excellent English
            elif ielts >= 6.0:
                score += 0.4  # Good English
            elif ielts >= 5.5:
                score += 0.3  # Acceptable English
            elif ielts > 0:
                score += 0.2  # Some English
        
        # Check German proficiency
        if "german" in supported_languages:
            german = (self.user_profile.get("german_level") or "none").lower()
            if german in ["c1", "c2"]:
                score += 0.5  # Advanced German
            elif german in ["b1", "b2"]:
                score += 0.4  # Intermediate German
            elif german in ["a1", "a2"]:
                score += 0.2  # Basic German
        
        # Check French proficiency
        if "french" in supported_languages:
            french = (self.user_profile.get("french_level") or "none").lower()
            if french in ["c1", "c2"]:
                score += 0.5  # Advanced French
            elif french in ["b1", "b2"]:
                score += 0.4  # Intermediate French
            elif french in ["a1", "a2"]:
                score += 0.2  # Basic French
        
        # Cap at 1.0
        return min(score, 1.0)
    
    def _score_financial_capacity(self, match_result: Dict[str, Any]) -> float:
        """
        Score financial capacity based on funds vs requirements.
        
        Args:
            match_result: Single MatchResult dict
            
        Returns:
            Score 0.0-1.0
        """
        gaps = match_result.get("rule_gaps", {})
        missing = gaps.get("missing_requirements", [])
        
        # Check if funds are mentioned in gaps
        has_funds_issue = any("funds" in req.lower() or "insufficient" in req.lower() 
                              for req in missing)
        
        if not has_funds_issue:
            return 1.0  # No financial issues
        
        # Parse gap amount if available
        user_funds = self.user_profile.get("funds_usd", 0)
        
        # Estimate based on match score
        raw_score = match_result.get("raw_score", 0.5)
        
        if raw_score >= 0.8:
            return 0.9  # Close to sufficient
        elif raw_score >= 0.6:
            return 0.7  # Moderate gap
        elif raw_score >= 0.4:
            return 0.5  # Significant gap
        else:
            return 0.3  # Large gap
    
    def _get_country_factor(self, country: str, factor: str) -> float:
        """
        Get a specific factor score for a country.
        
        Args:
            country: Country name
            factor: Factor name (visa_difficulty, quality_of_life, etc.)
            
        Returns:
            Score 0.0-1.0 (default 0.5 if not found)
        """
        country_data = self.COUNTRY_DATA.get(country, {})
        return country_data.get(factor, 0.5)
    
    def _calculate_final_score(self, match_result: Dict[str, Any]) -> float:
        """
        Calculate final weighted score (0-100) for a country.
        
        Args:
            match_result: Single MatchResult dict
            
        Returns:
            Final score 0-100
        """
        country = match_result.get("country", "")
        
        # Calculate individual factor scores
        factors = {
            "eligibility": self._score_eligibility(match_result),
            "language_alignment": self._score_language_alignment(country),
            "financial_capacity": self._score_financial_capacity(match_result),
            "visa_difficulty": self._get_country_factor(country, "visa_difficulty"),
            "quality_of_life": self._get_country_factor(country, "quality_of_life"),
            "cost_of_living": self._get_country_factor(country, "cost_of_living"),
            "job_market": self._get_country_factor(country, "job_market"),
        }
        
        # Calculate weighted sum
        weighted_score = sum(
            self.WEIGHTS[factor] * score 
            for factor, score in factors.items()
        )
        
        # Convert to 0-100 scale
        final_score = weighted_score * 100
        
        return round(final_score, 2)
    
    def _classify_countries(self, scored_countries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Classify countries into best/acceptable/not recommended.
        
        Args:
            scored_countries: List of dicts with country, score, etc.
            
        Returns:
            Classification dict
        """
        best_options = []
        acceptable = []
        not_recommended = []
        
        for item in scored_countries:
            country = item["country"]
            score = item["score"]
            
            if score >= self.BEST_THRESHOLD:
                best_options.append({
                    "country": country,
                    "score": score,
                    "reason": self._generate_reason(item, "best")
                })
            elif score >= self.ACCEPTABLE_THRESHOLD:
                acceptable.append({
                    "country": country,
                    "score": score,
                    "reason": self._generate_reason(item, "acceptable")
                })
            else:
                not_recommended.append(country)
        
        return {
            "best_options": best_options,
            "acceptable": acceptable,
            "not_recommended": not_recommended,
        }
    
    def _generate_reason(self, scored_item: Dict[str, Any], category: str) -> str:
        """
        Generate a brief reason for the score/category.
        
        Args:
            scored_item: Dict with country, score, match_result
            category: "best" or "acceptable"
            
        Returns:
            Reason string
        """
        country = scored_item["country"]
        score = scored_item["score"]
        match_result = scored_item.get("match_result", {})
        status = match_result.get("status", "Unknown")
        
        if category == "best":
            return (
                f"Strong match with eligibility status '{status}', "
                f"good language alignment, and favorable conditions."
            )
        else:  # acceptable
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
        
        Returns:
            {
                "best_options": [...],
                "acceptable": [...],
                "not_recommended": [...],
                "scores": {"Country": score, ...},
                "detailed_breakdown": [...]  # For debugging/transparency
            }
        """
        scored_countries = []
        scores_dict = {}
        
        # Calculate score for each match result
        for match_result in self.match_results:
            country = match_result.get("country")
            if not country:
                continue
            
            final_score = self._calculate_final_score(match_result)
            
            scored_countries.append({
                "country": country,
                "score": final_score,
                "match_result": match_result,
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
            
            detailed_breakdown.append({
                "country": country,
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
        
        return {
            "best_options": classification["best_options"],
            "acceptable": classification["acceptable"],
            "not_recommended": classification["not_recommended"],
            "scores": scores_dict,
            "detailed_breakdown": detailed_breakdown,
        }
    
    def get_top_recommendation(self) -> Optional[str]:
        """
        Get the single best recommended country.
        
        Returns:
            Country name or None if no good options
        """
        ranking = self.rank_countries()
        
        best = ranking.get("best_options", [])
        if best:
            return best[0]["country"]
        
        acceptable = ranking.get("acceptable", [])
        if acceptable:
            return acceptable[0]["country"]
        
        return None
