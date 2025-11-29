# tools/funds_gap_calculator.py

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
        """
        Initialize calculator with configurable thresholds.

        Args:
            threshold_ok: Coverage ratio for OK status (default: 1.0 = 100%)
            threshold_near: Coverage ratio for NEAR status (default: 0.8 = 80%)
            threshold_underfunded: Coverage ratio for UNDERFUNDED status (default: 0.5 = 50%)
        """
        self.threshold_ok = threshold_ok
        self.threshold_near = threshold_near
        self.threshold_underfunded = threshold_underfunded

        # Optional logger (high-level only)
        self.logger = Logger() if LOGGING_ENABLED and Logger is not None else None

        if self.logger:
            self.logger.log_tool_call(
                "FundsGapCalculator.__init__",
                {
                    "threshold_ok": threshold_ok,
                    "threshold_near": threshold_near,
                    "threshold_underfunded": threshold_underfunded,
                },
            )

    # ------------------------------------------------
    # GAP CALCULATION
    # ------------------------------------------------
    def calculate_gap(
        self,
        available: float,
        required: float,
        currency: str = "USD"
    ) -> Dict[str, Any]:
        """
        Calculate funding gap and provide comprehensive analysis.
        """
        if self.logger:
            self.logger.log_tool_call(
                "FundsGapCalculator.calculate_gap",
                {"available": available, "required": required, "currency": currency},
            )

        if available < 0 or required < 0:
            error = ValueError("Available and required funds must be non-negative.")
            if self.logger:
                self.logger.log_exception(error, "calculate_gap input validation")
            raise error

        # Edge case: no requirement
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

        # Calculate gap and coverage
        raw_gap = required - available
        gap = round(max(raw_gap, 0.0), 2)
        coverage = available / required  # 0.0 → 1.0+
        coverage_percent = round(coverage * 100, 2)

        # Determine status and suggestion
        if coverage >= self.threshold_ok:
            status = "OK"
            suggestion = (
                "Your available funds meet or exceed the recommended minimum. "
                "You're in a good position to proceed with your application."
            )
        elif coverage >= self.threshold_near:
            status = "NEAR"
            percentage_short = round((1 - coverage) * 100, 1)
            suggestion = (
                f"You have {coverage_percent}% of recommended funds ({percentage_short}% short). "
                "Consider a bit more saving, exploring scholarship options, "
                "or choosing a slightly more affordable program."
            )
        elif coverage >= self.threshold_underfunded:
            status = "UNDERFUNDED"
            suggestion = (
                f"You have {coverage_percent}% of recommended funds. "
                "Significant savings needed. Consider: part-time work, scholarships, "
                "cheaper accommodation, or delaying the application to save more."
            )
        else:
            status = "CRITICAL"
            suggestion = (
                f"You have only {coverage_percent}% of recommended funds. "
                "This pathway may not be feasible at the moment. "
                "Consider: alternative destinations with lower costs, extensive scholarships, "
                "or saving for 1–2 years before applying."
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

    # ------------------------------------------------
    # MONTHLY NEEDS
    # ------------------------------------------------
    def calculate_monthly_needs(
        self,
        country: str,
        duration_months: int = 12,
        include_buffer: bool = True
    ) -> Dict[str, Any]:
        """
        Estimate monthly and total living costs for a country.
        """
        if self.logger:
            self.logger.log_tool_call(
                "FundsGapCalculator.calculate_monthly_needs",
                {
                    "country": country,
                    "duration": duration_months,
                    "include_buffer": include_buffer,
                },
            )

        # Approximate average monthly costs (USD) - Updated for 2024
        living_costs = {
            "Canada": {"cost": 1500, "source": "official", "city": "average"},
            "USA": {"cost": 2000, "source": "official", "city": "average"},
            "Germany": {"cost": 1200, "source": "official", "city": "average"},
            "Netherlands": {"cost": 1400, "source": "official", "city": "average"},
            "Ireland": {"cost": 1500, "source": "official", "city": "average"},
            "Sweden": {"cost": 1600, "source": "official", "city": "average"},
            "Australia": {"cost": 1800, "source": "official", "city": "average"},
            "New Zealand": {"cost": 1600, "source": "official", "city": "average"},
        }

        country_data = living_costs.get(
            country,
            {"cost": 1500, "source": "estimated", "city": "average"},
        )
        monthly = float(country_data["cost"])

        # Add buffer if requested
        if include_buffer:
            monthly *= 1.2  # 20% safety buffer

        total = round(monthly * duration_months, 2)

        return {
            "country": country,
            "monthly_cost": round(monthly, 2),
            "duration_months": duration_months,
            "total_cost": total,
            "buffer_included": include_buffer,
            "year": 2024,
            "source": country_data.get("source", "estimated"),
        }

    # ------------------------------------------------
    # TOTAL NEEDS (LIVING + TUITION)
    # ------------------------------------------------
    def calculate_total_needs(
        self,
        country: str,
        pathway: str,
        duration_months: int = 12,
        include_tuition: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate TOTAL needs including living costs and tuition.
        """
        if self.logger:
            self.logger.log_tool_call(
                "FundsGapCalculator.calculate_total_needs",
                {
                    "country": country,
                    "pathway": pathway,
                    "duration": duration_months,
                },
            )

        # Living costs (always with buffer=True for safety plan)
        living = self.calculate_monthly_needs(country, duration_months, include_buffer=True)
        living_cost = living["total_cost"]

        # Tuition (if Study pathway)
        tuition = 0.0
        if pathway == "Study" and include_tuition:
            tuition_costs = {
                "Canada": 15000,
                "USA": 30000,
                "Germany": 0,          # Free for public universities
                "Netherlands": 12000,
                "Ireland": 14000,
                "Sweden": 0,           # Often free or low cost for EU/EEA
                "Australia": 20000,
                "New Zealand": 18000,
            }
            tuition = tuition_costs.get(country, 10000)

            # Prorate if less than 12 months
            if duration_months < 12 and duration_months > 0:
                tuition = (tuition / 12) * duration_months

        total = living_cost + tuition

        notes = None
        if country in ["Germany", "Sweden"]:
            notes = "Germany and Sweden often offer free or very low tuition at public universities."

        return {
            "country": country,
            "pathway": pathway,
            "living_cost": round(living_cost, 2),
            "tuition_cost": round(tuition, 2),
            "total_needed": round(total, 2),
            "breakdown": {
                "monthly_living": living["monthly_cost"],
                "duration_months": duration_months,
                "annual_tuition": round(
                    tuition * (12 / duration_months), 2
                ) if duration_months > 0 else 0,
            },
            "notes": notes,
        }

    # ------------------------------------------------
    # AFFORDABILITY COMPARISON
    # ------------------------------------------------
    def compare_affordability(
        self,
        available_funds: float,
        countries: list,
        pathway: str = "Study",
        duration_months: int = 12
    ) -> Dict[str, Any]:
        """
        Compare affordability across multiple countries.
        """
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
            # Calculate total needs
            needs = self.calculate_total_needs(country, pathway, duration_months)
            total_needed = needs["total_needed"]

            # Calculate gap
            gap_analysis = self.calculate_gap(available_funds, total_needed)

            results.append({
                "country": country,
                "total_needed": total_needed,
                "gap": gap_analysis["gap"],
                "status": gap_analysis["status"],
                "coverage_percent": gap_analysis["coverage_percent"],
                "affordable": gap_analysis["status"] in ["OK", "NEAR"],
            })

        # Sort by affordability (least gap first)
        results.sort(key=lambda x: x["gap"])
        most_affordable = results[0]["country"] if results else None

        # Recommendations
        recommendations = [
            f"{r['country']}: {r['status']} ({r['coverage_percent']}% covered)"
            for r in results
            if r["affordable"]
        ]

        return {
            "available_funds": available_funds,
            "countries": results,
            "most_affordable": most_affordable,
            "recommendations": recommendations if recommendations else ["Consider saving more funds"],
            "pathway": pathway,
            "duration_months": duration_months,
        }

    # ------------------------------------------------
    # SAVINGS PLAN
    # ------------------------------------------------
    def get_savings_plan(
        self,
        available: float,
        required: float,
        monthly_savings: float,
        currency: str = "USD"
    ) -> Dict[str, Any]:
        """
        Calculate savings plan to reach required funds.
        """
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
                "currency": currency,
            }

        if monthly_savings <= 0:
            return {
                "gap": gap,
                "monthly_savings": 0,
                "months_needed": None,
                "feasible": False,
                "feasibility_level": "Not feasible",
                "recommendation": "Savings plan not feasible without monthly savings capacity.",
                "currency": currency,
            }

        months_needed = int(gap / monthly_savings) + 1

        # Feasibility level
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
            f"{feasibility}. Consider: increasing income, reducing expenses, "
            "or choosing a more affordable destination."
        )

        return {
            "gap": round(gap, 2),
            "monthly_savings": monthly_savings,
            "months_needed": months_needed,
            "feasible": months_needed <= 24,
            "feasibility_level": feasibility,
            "recommendation": recommendation,
            "currency": currency,
        }
