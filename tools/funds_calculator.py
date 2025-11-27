# tools/funds_calculator.py

import sys
from pathlib import Path

# Add project root so we can import tools, rules, agents, ...
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from typing import Dict, Any, Optional

# ==================================================
# OPTIONAL LOGGER (Safe Import)
# ==================================================

from tools.logger import Logger, LOGGING_ENABLED

LOGGING_ENABLED = False
# ==================================================


class FundsGapCalculator:
    """
    Calculates the financial gap between available and required funds
    and provides status + suggestions with enhanced features.
    """

    def __init__(
        self,
        threshold_ok: float = 1.0,
        threshold_near: float = 0.8,
        threshold_underfunded: float = 0.5
    ):
        """Initialize calculator with configurable thresholds."""
        self.threshold_ok = threshold_ok
        self.threshold_near = threshold_near
        self.threshold_underfunded = threshold_underfunded

        self.logger = Logger() if LOGGING_ENABLED else None

        # High-level init log
        if self.logger:
            self.logger.log_tool_call(
                "FundsGapCalculator.__init__",
                {
                    "threshold_ok": threshold_ok,
                    "threshold_near": threshold_near,
                    "threshold_underfunded": threshold_underfunded,
                },
            )

    def calculate_gap(
        self,
        available: float,
        required: float,
        currency: str = "USD"
    ) -> Dict[str, Any]:

        # High-level logging
        if self.logger:
            self.logger.log_tool_call(
                "FundsGapCalculator.calculate_gap",
                {"available": available, "required": required, "currency": currency},
            )

        if available < 0 or required < 0:
            error = ValueError("Available and required funds must be non-negative.")
            if self.logger:
                self.logger.log_exception(error, "calculate_gap validation")
            raise error

        if required <= 0:
            return {
                "available": float(available),
                "required": float(required),
                "gap": 0.0,
                "coverage_percent": 100.0,
                "status": "OK",
                "suggestion": "No minimum funds are required for this pathway.",
                "currency": currency
            }

        raw_gap = required - available
        gap = round(max(raw_gap, 0.0), 2)
        coverage = available / required
        coverage_percent = round(coverage * 100, 2)

        if coverage >= self.threshold_ok:
            status = "OK"
            suggestion = (
                "Your available funds meet or exceed the recommended minimum. "
                "You're in a good position to proceed."
            )
        elif coverage >= self.threshold_near:
            status = "NEAR"
            percentage_short = round((1 - coverage) * 100, 1)
            suggestion = (
                f"You have {coverage_percent}% of recommended funds ({percentage_short}% short). "
                "Consider saving more or exploring affordable options."
            )
        elif coverage >= self.threshold_underfunded:
            status = "UNDERFUNDED"
            suggestion = (
                f"You have {coverage_percent}% of recommended funds. "
                "Significant savings needed."
            )
        else:
            status = "CRITICAL"
            suggestion = (
                f"You have only {coverage_percent}% of recommended funds. "
                "This pathway may not be feasible right now."
            )

        return {
            "available": float(available),
            "required": float(required),
            "gap": float(gap),
            "coverage_percent": coverage_percent,
            "status": status,
            "suggestion": suggestion,
            "currency": currency
        }

    def calculate_monthly_needs(
        self,
        country: str,
        duration_months: int = 12,
        include_buffer: bool = True
    ) -> Dict[str, Any]:

        if self.logger:
            self.logger.log_tool_call(
                "FundsGapCalculator.calculate_monthly_needs",
                {
                    "country": country,
                    "duration": duration_months,
                    "include_buffer": include_buffer,
                },
            )

        living_costs = {
            "Canada": {"cost": 1500},
            "USA": {"cost": 2000},
            "Germany": {"cost": 1200},
            "Netherlands": {"cost": 1400},
            "Ireland": {"cost": 1500},
            "Sweden": {"cost": 1600},
            "Australia": {"cost": 1800},
            "New Zealand": {"cost": 1600},
        }

        data = living_costs.get(country, {"cost": 1500})
        monthly = float(data["cost"])

        if include_buffer:
            monthly *= 1.2

        total = round(monthly * duration_months, 2)

        return {
            "country": country,
            "monthly_cost": round(monthly, 2),
            "duration_months": duration_months,
            "total_cost": total,
            "buffer_included": include_buffer,
            "year": 2024,
        }

    def calculate_total_needs(
        self,
        country: str,
        pathway: str,
        duration_months: int = 12,
        include_tuition: bool = True
    ) -> Dict[str, Any]:

        if self.logger:
            self.logger.log_tool_call(
                "FundsGapCalculator.calculate_total_needs",
                {
                    "country": country,
                    "pathway": pathway,
                    "duration": duration_months,
                },
            )

        living = self.calculate_monthly_needs(country, duration_months)
        living_cost = living["total_cost"]

        tuition = 0.0
        if pathway == "Study" and include_tuition:
            tuition_costs = {
                "Canada": 15000,
                "USA": 30000,
                "Germany": 0,
                "Netherlands": 12000,
                "Ireland": 14000,
                "Sweden": 0,
                "Australia": 20000,
                "New Zealand": 18000,
            }
            tuition = tuition_costs.get(country, 10000)

            if duration_months < 12:
                tuition = (tuition / 12) * duration_months

        total = living_cost + tuition

        return {
            "country": country,
            "pathway": pathway,
            "living_cost": round(living_cost, 2),
            "tuition_cost": round(tuition, 2),
            "total_needed": round(total, 2),
        }

    def compare_affordability(
        self,
        available_funds: float,
        countries: list,
        pathway: str = "Study",
        duration_months: int = 12
    ) -> Dict[str, Any]:

        if self.logger:
            self.logger.log_tool_call(
                "FundsGapCalculator.compare_affordability",
                {
                    "available_funds": available_funds,
                    "countries_count": len(countries),
                    "pathway": pathway,
                },
            )

        results = []

        for country in countries:
            needs = self.calculate_total_needs(country, pathway, duration_months)
            total_needed = needs["total_needed"]
            gap_data = self.calculate_gap(available_funds, total_needed)

            results.append({
                "country": country,
                "total_needed": total_needed,
                "gap": gap_data["gap"],
                "status": gap_data["status"],
                "coverage_percent": gap_data["coverage_percent"],
                "affordable": gap_data["status"] in ["OK", "NEAR"]
            })

        results.sort(key=lambda x: x["gap"])
        most_affordable = results[0]["country"] if results else None

        recommendations = [
            f"{r['country']}: {r['status']} ({r['coverage_percent']}%)"
            for r in results
            if r["affordable"]
        ]

        return {
            "available_funds": available_funds,
            "countries": results,
            "most_affordable": most_affordable,
            "recommendations": recommendations if recommendations else ["Consider saving more funds"],
            "pathway": pathway,
            "duration_months": duration_months
        }

    def get_savings_plan(
        self,
        available: float,
        required: float,
        monthly_savings: float,
        currency: str = "USD"
    ) -> Dict[str, Any]:

        if self.logger:
            self.logger.log_tool_call(
                "FundsGapCalculator.get_savings_plan",
                {
                    "available": available,
                    "required": required,
                    "monthly_savings": monthly_savings,
                },
            )

        gap = max(required - available, 0)

        if gap == 0:
            return {
                "gap": 0.0,
                "monthly_savings": monthly_savings,
                "months_needed": 0,
                "feasible": True,
                "feasibility_level": "Already sufficient",
                "recommendation": "You already have sufficient funds!",
                "currency": currency
            }

        if monthly_savings <= 0:
            return {
                "gap": gap,
                "monthly_savings": 0,
                "months_needed": None,
                "feasible": False,
                "feasibility_level": "Not feasible",
                "recommendation": "Savings plan not feasible without monthly savings.",
                "currency": currency
            }

        months_needed = int(gap / monthly_savings) + 1

        if months_needed <= 6:
            feasibility = "Highly feasible"
        elif months_needed <= 12:
            feasibility = "Feasible"
        elif months_needed <= 24:
            feasibility = "Challenging but possible"
        else:
            feasibility = "Very challenging"

        recommendation = (
            f"Save {monthly_savings} {currency}/month for {months_needed} months. "
            f"{feasibility}. Consider increasing income or choosing a more affordable destination."
        )

        return {
            "gap": round(gap, 2),
            "monthly_savings": monthly_savings,
            "months_needed": months_needed,
            "feasible": months_needed <= 24,
            "feasibility_level": feasibility,
            "recommendation": recommendation,
            "currency": currency
        }
