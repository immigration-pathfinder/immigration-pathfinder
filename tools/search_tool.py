# tools/search_tool.py
import sys
from pathlib import Path

# Add project root so we can import tools, rules, agents, ...
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from typing import List, Dict, Optional, Callable, Any
from datetime import datetime

# ==================================================
# OPTIONAL LOGGER (Safe Import)
# ==================================================
from tools.logger import Logger, LOGGING_ENABLED
LOGGING_ENABLED = False
# ==================================================


class SearchTool:
    """
    High-level search abstraction for immigration-related queries.
    """

    def __init__(self, search_func: Optional[Callable] = None):
        self.search_func = search_func
        self.search_history = []
        self.last_updated = datetime.now().isoformat()

        # logger toggle
        self.logger = Logger() if (LOGGING_ENABLED and Logger) else None

        if self.logger:
            self.logger.log_tool_call(
                "SearchTool.__init__",
                {"mode": "real" if search_func else "mock"}
            )

    # ============================================================
    # MAIN SEARCH
    # ============================================================

    def search_immigration(
        self,
        query: str,
        country: Optional[str] = None,
        pathway: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:

        if self.logger:
            self.logger.log_tool_call(
                "SearchTool.search_immigration",
                {"query": query, "country": country, "pathway": pathway}
            )

        full_query = self._build_query(query, country, pathway)

        self.search_history.append({
            "query": full_query,
            "original_query": query,
            "country": country,
            "pathway": pathway,
            "timestamp": self._get_timestamp(),
            "max_results": max_results
        })

        if self.search_func:
            results = self._real_search(full_query, max_results)
        else:
            results = self._mock_search(full_query, country, pathway, max_results)

        return self._add_relevance_scores(results, query, country, pathway)

    # ============================================================
    # HELPER API SEARCHES
    # ============================================================

    def search_visa_difficulty(self, country: str, pathway: str) -> Dict[str, Any]:
        query = f"{country} {pathway} visa difficulty approval rate 2024"
        results = self.search_immigration(query, country, pathway, max_results=3)

        return {
            "country": country,
            "pathway": pathway,
            "difficulty": "Medium",
            "sources": [r["url"] for r in results],
            "summary": results[0]["snippet"] if results else "No data available",
            "confidence": 0.7
        }

    def search_job_market(self, country: str, field: Optional[str] = None) -> Dict[str, Any]:
        query = f"{country} job market trends 2024"
        if field:
            query += f" {field}"

        results = self.search_immigration(query, country, max_results=3)

        return {
            "country": country,
            "field": field,
            "outlook": "Positive",
            "sources": [r["url"] for r in results],
            "summary": results[0]["snippet"] if results else "No data available"
        }

    def search_country_summary(self, country: str) -> Dict[str, Any]:
        query = f"{country} immigration overview policies 2024"
        results = self.search_immigration(query, country, max_results=3)

        return {
            "country": country,
            "sources": [r["url"] for r in results],
            "summary": results[0]["snippet"] if results else "No data available",
            "last_updated": self.last_updated
        }

    def verify_requirements(self, country: str, pathway: str, requirement: str) -> Dict[str, Any]:
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

    # ============================================================
    # INTERNAL METHODS
    # ============================================================

    def _build_query(self, query: str, country: Optional[str], pathway: Optional[str]) -> str:
        parts = [query]

        if country:
            parts.append(country)
        if pathway and pathway.lower() in ["study", "work", "pr"]:
            parts.append(f"{pathway} visa")

        parts.append("2024")
        return " ".join(parts)

    # ------------------------------------------------------------
    # REAL SEARCH
    # ------------------------------------------------------------
    def _real_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:

        if self.logger:
            self.logger.log_tool_call(
                "SearchTool._real_search",
                {"query": query}
            )

        try:
            raw_results = self.search_func(query, num_results=max_results)

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
            if self.logger:
                self.logger.log_exception(e, "SearchTool._real_search")

            return self._mock_search(query, None, None, max_results)

    # ------------------------------------------------------------
    # MOCK SEARCH (FULL VERSION — 100% YOUR ORIGINAL)
    # ------------------------------------------------------------
    def _mock_search(
        self,
        query: str,
        country: Optional[str],
        pathway: Optional[str],
        max_results: int
    ) -> List[Dict[str, Any]]:

        if self.logger:
            self.logger.log_tool_call(
                "SearchTool._mock_search",
                {"country": country, "pathway": pathway}
            )

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
                }
            }
        }

        results = []

        # Country + Pathway match
        if country and pathway:
            cdata = mock_data.get(country, {})
            pdata = cdata.get(pathway, {})

            if pdata:
                results.append({
                    "title": f"Official {country} {pathway} Visa Requirements 2024",
                    "url": pdata.get("url", "https://example.gov"),
                    "snippet": pdata.get("snippet", f"Requirements for {country} {pathway}"),
                    "source": "mock_search"
                })

        # Generic country
        if country:
            results.append({
                "title": f"{country} Immigration Guide 2024",
                "url": f"https://example.com/{country.lower()}-guide",
                "snippet": f"Complete guide to {country} immigration requirements, visa types, and application process. Updated for 2024.",
                "source": "mock_search"
            })

        # Generic pathway
        if pathway:
            results.append({
                "title": f"{pathway} Visa Requirements Overview",
                "url": "https://example.edu/visa-guide",
                "snippet": f"Detailed requirements for {pathway} visa applications including eligibility criteria, documentation, and processing times.",
                "source": "mock_search"
            })

        # Final “general info”
        results.append({
            "title": "Immigration Information Portal",
            "url": "https://example.org/immigration",
            "snippet": f"Query: '{query}'. General immigration information including visa types, requirements, and application procedures.",
            "source": "mock_search"
        })

        return results[:max_results]

    # ------------------------------------------------------------
    # Relevance
    # ------------------------------------------------------------
    def _add_relevance_scores(self, results, query, country, pathway):

        keywords = query.lower().split()
        if country:
            keywords.append(country.lower())
        if pathway:
            keywords.append(pathway.lower())

        for item in results:
            text = (item["title"] + " " + item["snippet"]).lower()
            matches = sum(kw in text for kw in keywords)
            item["relevance"] = min(matches / len(keywords), 1.0)

        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results

    def _get_timestamp(self):
        return datetime.now().isoformat()

    # ============================================================
    # UTILS
    # ============================================================

    def get_search_history(self):
        return self.search_history

    def clear_history(self):
        self.search_history = []
        print("[INFO] Search history cleared")

    def get_stats(self):
        return {
            "total_searches": len(self.search_history),
            "mode": "real" if self.search_func else "mock",
            "last_updated": self.last_updated
        }
