from typing import Any, Dict, List, Optional
from tools.logger import Logger


class SearchTool:
    """
    Simple search tool.
    In Kaggle environment, this could call Gemini or a real search API.
    Locally, we use a mock result so pipeline always works.
    """

    def __init__(self, logger: Optional[Logger] = None):
        # Default logger
        self.logger = logger or Logger()

    def search(self, query: str, country: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Perform a search and return structured results.

        In Kaggle:
            - This may call Gemini / web API
        Local:
            - Returns mock results
        """

        # ------------------------
        # Logging (Phase 3)
        # ------------------------
        if self.logger:
            self.logger.log_tool_call(
                tool_name="SearchTool",
                params={
                    "query": query[:120],      # short preview
                    "country": country or "N/A",
                },
            )

        # ------------------------
        # TODO: Real Gemini-based search for Kaggle
        # ------------------------
        # Example:
        #
        #   response = gemini_model.generate_content(...)
        #   parsed = json.loads(response.text)
        #   return parsed
        #
        # For now: use mock result
        return self._mock_search(query, country)

    def _mock_search(self, query: str, country: Optional[str]) -> List[Dict[str, Any]]:
        """
        Local mock search result.
        This ensures pipeline never breaks.
        """

        return [
            {
                "title": f"Mock result for '{query}'",
                "country": country,
                "score": 0.87,
                "details": "Mocked search response. Replace in Kaggle phase.",
            }
        ]
if __name__ == "__main__":
    tool = SearchTool()
    results = tool.search("visa requirements", "Germany")
    print(results)
