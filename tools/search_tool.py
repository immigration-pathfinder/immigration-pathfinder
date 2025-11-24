
# tools/search_tool.py

from typing import List, Dict, Optional, Callable, Any
from datetime import datetime


class SearchTool:
    """
    High-level search abstraction for immigration-related queries.
    
    Can work in two modes:
    1. Mock mode (for testing without real search)
    2. Real mode (with Google Search or Gemini)
    
    Usage:
        # Mock mode (testing)
        tool = SearchTool()
        
        # Real mode (with search function)
        def my_search(query, num_results=5):
            # Your search implementation
            return [{"title": "...", "url": "...", "snippet": "..."}]
        
        tool = SearchTool(search_func=my_search)
    """
    
    def __init__(self, search_func: Optional[Callable] = None):
        """
        Initialize SearchTool.
        
        Args:
            search_func: Optional search function.
                        Should accept (query: str, num_results: int)
                        Should return List[Dict] with keys: title, url, snippet
        """
        self.search_func = search_func
        self.search_history = []
        self.last_updated = datetime.now().isoformat()
    
    def search_immigration(
        self,
        query: str,
        country: Optional[str] = None,
        pathway: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for immigration-related information.
        
        Args:
            query: Search query string
            country: Optional country filter
            pathway: Optional pathway filter (Study/Work/PR)
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with structure:
            [
                {
                    "title": str,
                    "url": str,
                    "snippet": str,
                    "source": "real_search" | "mock_search",
                    "relevance": float (0-1)
                },
                ...
            ]
        """
        # Build enhanced query
        full_query = self._build_query(query, country, pathway)
        
        # Log search
        self.search_history.append({
            "query": full_query,
            "original_query": query,
            "country": country,
            "pathway": pathway,
            "timestamp": self._get_timestamp(),
            "max_results": max_results
        })
        
        # Execute search
        if self.search_func is not None:
            results = self._real_search(full_query, max_results)
        else:
            results = self._mock_search(full_query, country, pathway, max_results)
        
        # Add relevance scores
        results = self._add_relevance_scores(results, query, country, pathway)
        
        return results
    
    def search_visa_difficulty(self, country: str, pathway: str) -> Dict[str, Any]:
        """
        Search for visa difficulty information.
        
        Args:
            country: Country name
            pathway: Immigration pathway
            
        Returns:
            Dictionary with difficulty analysis
        """
        query = f"{country} {pathway} visa difficulty approval rate 2024"
        results = self.search_immigration(query, country, pathway, max_results=3)
        
        return {
            "country": country,
            "pathway": pathway,
            "difficulty": "Medium",  # Can be enhanced with Gemini analysis
            "sources": [r["url"] for r in results],
            "summary": results[0]["snippet"] if results else "No data available",
            "confidence": 0.7
        }
    
    def search_job_market(self, country: str, field: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for job market trends.
        
        Args:
            country: Country name
            field: Optional field of study/work
            
        Returns:
            Dictionary with job market analysis
        """
        query = f"{country} job market trends 2024"
        if field:
            query += f" {field}"
        
        results = self.search_immigration(query, country, max_results=3)
        
        return {
            "country": country,
            "field": field,
            "outlook": "Positive",  # Can be enhanced with Gemini analysis
            "sources": [r["url"] for r in results],
            "summary": results[0]["snippet"] if results else "No data available"
        }
    
    def search_country_summary(self, country: str) -> Dict[str, Any]:
        """
        Search for high-level country immigration summary.
        
        Args:
            country: Country name
            
        Returns:
            Dictionary with country summary
        """
        query = f"{country} immigration overview policies 2024"
        results = self.search_immigration(query, country, max_results=3)
        
        return {
            "country": country,
            "sources": [r["url"] for r in results],
            "summary": results[0]["snippet"] if results else "No data available",
            "last_updated": self.last_updated
        }
    
    def verify_requirements(
        self, 
        country: str, 
        pathway: str,
        requirement: str
    ) -> Dict[str, Any]:
        """
        Verify specific requirement (e.g., IELTS score).
        
        Args:
            country: Country name
            pathway: Immigration pathway
            requirement: Specific requirement to verify
            
        Returns:
            Verification result
        """
        query = f"{country} {pathway} visa {requirement} requirement official 2024"
        results = self.search_immigration(query, country, pathway, max_results=2)
        
        return {
            "country": country,
            "pathway": pathway,
            "requirement": requirement,
            "verified": True,
            "sources": [r["url"] for r in results],
            "notes": results[0]["snippet"] if results else "Could not verify",
            "confidence": 0.8 if results else 0.0
        }
    
    # ============== Internal Methods ==============
    
    def _build_query(
        self, 
        query: str, 
        country: Optional[str], 
        pathway: Optional[str]
    ) -> str:
        """Build enhanced search query."""
        parts = [query]
        
        if country:
            parts.append(country)
        
        if pathway and pathway.lower() in ["study", "work", "pr"]:
            parts.append(f"{pathway} visa")
        
        # Add year for current info
        parts.append("2024")
        
        return " ".join(parts)
    
    def _real_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Execute real search using provided search function.
        """
        try:
            # Call search function
            raw_results = self.search_func(query, num_results=max_results)
            
            # Normalize results to standard format
            normalized = []
            for item in raw_results:
                normalized.append({
                    "title": str(item.get("title") or item.get("name") or "Result"),
                    "url": str(item.get("link") or item.get("url") or ""),
                    "snippet": str(item.get("snippet") or item.get("description") or ""),
                    "source": "real_search"
                })
            
            return normalized if normalized else self._mock_search(query, None, None, max_results)
            
        except Exception as e:
            print(f"[WARNING] Search failed: {e}, falling back to mock")
            return self._mock_search(query, None, None, max_results)
    
    def _mock_search(
        self, 
        query: str, 
        country: Optional[str],
        pathway: Optional[str],
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Fallback mock search with realistic country-specific results.
        """
        # Country-specific mock data
        mock_data = {
            "Canada": {
                "Study": {
                    "snippet": "Canada Study Permit requires: Acceptance letter from DLI, proof of funds (CAD 20,635/year + tuition), IELTS 6.0 overall, clean criminal record, medical exam.",
                    "url": "https://www.canada.ca/en/immigration-refugees-citizenship/services/study-canada.html"
                },
                "Work": {
                    "snippet": "Canada Work Permit options: Express Entry (CRS 470+), Provincial Nominee Programs, LMIA-based permits. Processing time: 6-12 months.",
                    "url": "https://www.canada.ca/en/immigration-refugees-citizenship/services/work-canada.html"
                },
                "PR": {
                    "snippet": "Canada PR through Express Entry: CRS score 470+, language test (IELTS/CELPIP), ECA, proof of funds CAD 13,000+.",
                    "url": "https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada.html"
                }
            },
            "Germany": {
                "Study": {
                    "snippet": "Germany Study Visa: University admission, €11,208/year blocked account, health insurance (€110/month), no tuition for public universities.",
                    "url": "https://www.study-in-germany.de/en/"
                },
                "Work": {
                    "snippet": "Germany Blue Card: University degree, job offer €43,800+ salary (IT €40,770+), health insurance, German A1 level recommended.",
                    "url": "https://www.make-it-in-germany.com/"
                },
                "PR": {
                    "snippet": "Germany PR (Settlement Permit): 5 years residence, German B1, employment, pension contributions, housing.",
                    "url": "https://www.germany.info/"
                }
            },
            "USA": {
                "Study": {
                    "snippet": "USA F-1 Visa: I-20 form, SEVIS fee $350, proof of funds $30,000+/year, TOEFL 80+/IELTS 6.5+, visa interview.",
                    "url": "https://studyinthestates.dhs.gov/"
                },
                "Work": {
                    "snippet": "USA H-1B Visa: Bachelor's degree, employer sponsorship, $60,000+ salary, lottery system (33% approval rate).",
                    "url": "https://www.uscis.gov/"
                },
                "PR": {
                    "snippet": "USA Green Card: Employment-based (EB-1/2/3), family sponsorship, or diversity lottery. Wait time: 2-10 years.",
                    "url": "https://www.uscis.gov/green-card"
                }
            },
            "Netherlands": {
                "Study": {
                    "snippet": "Netherlands Study Visa: University admission, €11,400/year proof of funds, health insurance, IELTS 6.0+.",
                    "url": "https://www.studyinholland.nl/"
                },
            },
            "Australia": {
                "Study": {
                    "snippet": "Australia Student Visa (Subclass 500): CoE, GTE, funds AUD 24,505/year, IELTS 5.5+, OSHC insurance.",
                    "url": "https://www.studyaustralia.gov.au/"
                },
            }
        }
        
        # Generate results
        results = []
        
        # Try to get country-specific data
        if country and pathway:
            country_data = mock_data.get(country, {})
            pathway_data = country_data.get(pathway, {})
            
            if pathway_data:
                results.append({
                    "title": f"Official {country} {pathway} Visa Requirements 2024",
                    "url": pathway_data.get("url", "https://example.gov"),
                    "snippet": pathway_data.get("snippet", f"Requirements for {country} {pathway}"),
                    "source": "mock_search"
                })
        
        # Add generic results
        if country:
            results.append({
                "title": f"{country} Immigration Guide 2024",
                "url": f"https://example.com/{country.lower()}-guide",
                "snippet": f"Complete guide to {country} immigration requirements, visa types, and application process. Updated for 2024.",
                "source": "mock_search"
            })
        
        if pathway:
            results.append({
                "title": f"{pathway} Visa Requirements Overview",
                "url": "https://example.edu/visa-guide",
                "snippet": f"Detailed requirements for {pathway} visa applications including eligibility criteria, documentation, and processing times.",
                "source": "mock_search"
            })
        
        # Add general result
        results.append({
            "title": "Immigration Information Portal",
            "url": "https://example.org/immigration",
            "snippet": f"Query: '{query}'. General immigration information including visa types, requirements, and application procedures.",
            "source": "mock_search"
        })
        
        return results[:max_results]
    
    def _add_relevance_scores(
        self,
        results: List[Dict[str, Any]],
        query: str,
        country: Optional[str],
        pathway: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Add relevance scores based on keyword matching."""
        keywords = query.lower().split()
        if country:
            keywords.append(country.lower())
        if pathway:
            keywords.append(pathway.lower())
        
        for result in results:
            text = (result["title"] + " " + result["snippet"]).lower()
            matches = sum(1 for kw in keywords if kw in text)
            result["relevance"] = min(matches / len(keywords), 1.0)
        
        # Sort by relevance
        results.sort(key=lambda x: x["relevance"], reverse=True)
        
        return results
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        return datetime.now().isoformat()
    
    # ============== Utility Methods ==============
    
    def get_search_history(self) -> List[Dict[str, Any]]:
        """
        Get history of all searches.
        
        Returns:
            List of search records
        """
        return self.search_history
    
    def clear_history(self):
        """Clear search history."""
        self.search_history = []
        print("[INFO] Search history cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get search statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "total_searches": len(self.search_history),
            "mode": "real" if self.search_func else "mock",
            "last_updated": self.last_updated
        }
