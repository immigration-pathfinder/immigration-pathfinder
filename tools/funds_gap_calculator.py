from typing import Any, Dict, Optional
from tools.logger import Logger


class FundsGapCalculator:
    """
    Simple tool that calculates:
      - estimated required settlement funds (mock)
      - gap between required funds and current savings

    In Kaggle, this can be replaced with real tables / APIs.
    Locally we keep it simple so the pipeline always runs.
    """

    def __init__(self, logger: Optional[Logger] = None) -> None:
        # Use shared project logger if provided, otherwise create a local one
        self.logger = logger or Logger()

    def calculate_required_funds(
        self,
        country: str,
        adults: int = 1,
        children: int = 0,
    ) -> Dict[str, Any]:
        """
        Return a mock estimation for required settlement funds.

        adults: number of adult applicants
        children: number of children
        """

        # ---- Logging (Phase 3) ----
        if self.logger:
            self.logger.log_tool_call(
                tool_name="FundsGapCalculator.calculate_required_funds",
                params={
                    "country": country,
                    "adults": adults,
                    "children": children,
                },
            )

        # ---- Mock logic: simple formula ----
        base_amount = 12000  # USD for 1 adult
        total = base_amount + (adults - 1) * 8000 + children * 5000

        return {
            "country": country,
            "adults": adults,
            "children": children,
            "estimated_required_funds_usd": total,
            "note": "Mock calculation. Replace with real data in Kaggle Phase 4.",
        }

    def calculate_funds_gap(
        self,
        country: str,
        current_savings_usd: float,
        adults: int = 1,
        children: int = 0,
    ) -> Dict[str, Any]:
        """
        Calculate gap between required funds and current savings.
        """

        # ---- Logging (Phase 3) ----
        if self.logger:
            self.logger.log_tool_call(
                tool_name="FundsGapCalculator.calculate_funds_gap",
                params={
                    "country": country,
                    "current_savings_usd": current_savings_usd,
                    "adults": adults,
                    "children": children,
                },
            )

        required = self.calculate_required_funds(
            country=country,
            adults=adults,
            children=children,
        )

        gap = required["estimated_required_funds_usd"] - current_savings_usd

        return {
            "country": country,
            "adults": adults,
            "children": children,
            "required_funds_usd": required["estimated_required_funds_usd"],
            "current_savings_usd": current_savings_usd,
            "gap_usd": gap,
            "is_enough": gap <= 0,
        }


if __name__ == "__main__":
    calc = FundsGapCalculator()
    result = calc.calculate_funds_gap(
        "Germany",
        current_savings_usd=8000,
        adults=2,
        children=1,
    )
    print(result)
