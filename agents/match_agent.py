from typing import Any, Dict, List, Optional
from tools.logger import Logger


class MatchAgent:
    """
    MatchAgent

    Phase 5:
      - Input: structured profile from ProfileAgent
      - Output: a very simple, rule-based mock "eligibility" result.

    اینجا عمداً منطق واقعی ویزا پیاده نشده.
    فقط یک موتور قانون ساده است برای دمو و فاز کگل.
    """

    def __init__(self, logger: Optional[Logger] = None) -> None:
        self.logger = logger or Logger()

    def run(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        # ---- Logging ----
        if self.logger:
            self.logger.log_agent_call(
                agent_name="MatchAgent",
                session_id=None,
                input_summary=str({
                    k: profile.get(k, None)
                    for k in [
                        "age",
                        "citizenship",
                        "education_level",
                        "field_of_study",
                        "english_level",
                        "funds_usd",
                        "work_experience_years",
                        "goal",
                        "target_countries",
                    ]
                })[:200],
            )

        # ---- Extract fields from profile ----
        age = profile.get("age")
        citizenship = profile.get("citizenship")
        education_level = (profile.get("education_level") or "").lower()
        field_of_study = profile.get("field_of_study")
        english_level = (profile.get("english_level") or "").upper()
        funds_usd = profile.get("funds_usd")
        work_experience_years = profile.get("work_experience_years") or 0.0
        goal = (profile.get("goal") or "").lower()
        target_countries: List[str] = profile.get("target_countries") or []

        reasons: List[str] = []

        # ---- Simple mock rules (Phase 5 demo) ----

        # فقط مسیر Work را پشتیبانی می‌کنیم
        if goal != "work":
            return {
                "eligible_countries": [],
                "reasoning": (
                    "Mock rules currently only support work pathways. "
                    f"Detected goal='{goal}'."
                ),
            }

        # شرط سنی (صرفاً برای دمو)
        if age is None:
            reasons.append("Age is missing.")
        elif age > 45:
            reasons.append("Age is above 45, which is harder for many work visas.")

        # مدرک تحصیلی
        if education_level not in {"bachelor", "master", "phd"}:
            reasons.append(
                "Education level is below bachelor or was not recognized "
                f"(detected: '{education_level or 'none'}')."
            )

        # زبان انگلیسی
        if english_level not in {"B1", "B2", "C1", "C2"}:
            reasons.append(
                "English level is below B1 or was not recognized "
                f"(detected: '{english_level or 'none'}')."
            )

        # تمکن مالی
        if not funds_usd or funds_usd < 8000:
            reasons.append(
                "Available funds are below 8,000 USD (or not detected)."
            )

        # سابقه کار
        if work_experience_years < 1:
            reasons.append(
                "Work experience is less than 1 year "
                f"(detected: {work_experience_years})."
            )

        # اگر هیچ محدودیتی نبود، کشورهای هدف را واجد شرایط اعلام کن
        if not reasons:
            eligible_countries = target_countries
        else:
            eligible_countries = []

        # متن توضیح
        if eligible_countries:
            reasoning = (
                "Mock rule engine (Phase 5) marked the target countries as eligible. "
                "All basic conditions (education, English, funds, experience) were met "
                "based on the extracted profile."
            )
        else:
            reasoning = (
                "Mock rule engine (Phase 5) did not find an eligible country. "
                "Limitations for eligibility: " + "; ".join(reasons)
            )

        return {
            "eligible_countries": eligible_countries,
            "reasoning": reasoning,
        }
