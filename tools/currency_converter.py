# tools/currency_converter.py

import sys
from pathlib import Path

# Add project root so we can import tools, rules, agents, ...
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from typing import Dict, Any, Optional
from datetime import datetime

# ==================================================
# OPTIONAL LOGGER (Safe Import)
# ==================================================
from tools.logger import Logger, LOGGING_ENABLED
LOGGING_ENABLED = False
# ==================================================


class CurrencyConverter:
    """
    Currency converter for normalizing amounts to USD.

    Uses static exchange rates suitable for MVP/offline environments.
    For production, can be extended with live FX API integration.
    """

    def __init__(self, last_updated: Optional[str] = None):
        """
        Initialize with exchange rates.
        """
        self.last_updated = last_updated or "2024-11-24"
        self.logger = Logger() if LOGGING_ENABLED else None

        # Exchange rates: 1 unit of currency ≈ rate USD
        self.rates_to_usd: Dict[str, float] = {
            "USD": 1.0,
            "EUR": 1.10,
            "GBP": 1.27,
            "CAD": 0.75,
            "AUD": 0.65,
            "NZD": 0.60,

            "CHF": 1.15,
            "SEK": 0.095,
            "NOK": 0.092,
            "DKK": 0.147,

            "CNY": 0.14,
            "JPY": 0.0067,
            "INR": 0.012,
            "SGD": 0.74,
            "HKD": 0.128,
            "KRW": 0.00076,

            "AED": 0.27,
            "SAR": 0.27,
            "ILS": 0.27,
            "IRR": 0.000020,

            "BRL": 0.20,
            "MXN": 0.059,
            "ARS": 0.0011,

            "ZAR": 0.055,
            "TRY": 0.034,
            "RUB": 0.010,
        }

        print(f"[INFO] Currency rates initialized (last updated: {self.last_updated})")

        if self.logger:
            self.logger.log_tool_call(
                "CurrencyConverter.__init__",
                {"last_updated": self.last_updated, "currency_count": len(self.rates_to_usd)},
            )

    # ------------------------------------------------
    # Conversion Methods
    # ------------------------------------------------
    def convert(
        self,
        amount: float,
        from_curr: str,
        to_curr: str = "USD",
        decimals: int = 2
    ) -> float:
        """
        Convert amount between currencies.
        """
        if amount < 0:
            raise ValueError("Amount must be non-negative.")

        if amount == 0:
            return 0.0

        if amount > 1e12:
            raise ValueError("Amount is unrealistically large (> 1 trillion).")

        from_curr = from_curr.upper()
        to_curr = to_curr.upper()

        if from_curr not in self.rates_to_usd:
            raise ValueError(f"Unsupported currency: {from_curr}. Supported: {self._get_supported_list()}")

        if to_curr not in self.rates_to_usd:
            raise ValueError(f"Unsupported currency: {to_curr}. Supported: {self._get_supported_list()}")

        # Convert: source → USD → target
        amount_in_usd = amount * self.rates_to_usd[from_curr]

        if to_curr == "USD":
            target_amount = amount_in_usd
        else:
            target_amount = amount_in_usd / self.rates_to_usd[to_curr]

        return round(target_amount, decimals)

    def normalize_to_usd(self, amount: float, currency: str) -> float:
        """Shortcut: convert any currency → USD"""
        return self.convert(amount, currency, "USD")

    def convert_with_info(
        self,
        amount: float,
        from_curr: str,
        to_curr: str = "USD"
    ) -> Dict[str, Any]:
        """
        Convert and return detailed calculation info.
        """
        converted = self.convert(amount, from_curr, to_curr)

        from_curr = from_curr.upper()
        to_curr = to_curr.upper()

        rate_from = self.rates_to_usd[from_curr]
        rate_to = self.rates_to_usd[to_curr]
        effective_rate = rate_from / rate_to

        return {
            "original_amount": amount,
            "original_currency": from_curr,
            "converted_amount": converted,
            "converted_currency": to_curr,
            "exchange_rate": round(effective_rate, 6),
            "last_updated": self.last_updated,
            "calculation": f"{amount} {from_curr} × {effective_rate:.4f} = {converted} {to_curr}"
        }

    # ------------------------------------------------
    # Info Methods
    # ------------------------------------------------
    def get_supported_currencies(self) -> Dict[str, float]:
        return self.rates_to_usd.copy()

    def get_currency_info(self, currency: str) -> Dict[str, Any]:
        currency = currency.upper()

        if currency not in self.rates_to_usd:
            return {
                "code": currency,
                "supported": False,
                "message": f"Currency not supported. Try: {self._get_supported_list()}"
            }

        rate = self.rates_to_usd[currency]

        return {
            "code": currency,
            "rate_to_usd": rate,
            "usd_to_currency": round(1 / rate, 6),
            "supported": True,
            "last_updated": self.last_updated,
            "example": f"1 {currency} = {rate} USD, 1 USD = {round(1/rate, 2)} {currency}"
        }

    # ------------------------------------------------
    # Update Rate
    # ------------------------------------------------
    def update_rate(self, currency: str, rate: float, source: str = "manual"):
        currency = currency.upper()
        old_rate = self.rates_to_usd.get(currency, "N/A")

        self.rates_to_usd[currency] = rate
        self.last_updated = datetime.now().strftime("%Y-%m-%d")

        print(f"[INFO] Updated {currency} rate: {old_rate} → {rate} (source: {source})")

        if self.logger:
            self.logger.log_tool_call(
                "CurrencyConverter.update_rate",
                {
                    "currency": currency,
                    "old_rate": old_rate,
                    "new_rate": rate,
                    "source": source,
                    "last_updated": self.last_updated,
                },
            )

    # ------------------------------------------------
    # Bulk Conversion
    # ------------------------------------------------
    def bulk_convert(
        self,
        amounts: Dict[str, float],
        to_curr: str = "USD"
    ) -> Dict[str, float]:

        if self.logger:
            self.logger.log_tool_call(
                "CurrencyConverter.bulk_convert",
                {"len_amounts": len(amounts), "to_curr": to_curr},
            )

        results = {}

        for currency, amount in amounts.items():
            try:
                results[currency] = self.convert(amount, currency, to_curr)
            except ValueError as e:
                if self.logger:
                    self.logger.log_exception(e, f"bulk_convert:{currency}")
                results[currency] = f"Error: {e}"

        return results

    # ------------------------------------------------
    # Compare Currencies
    # ------------------------------------------------
    def compare_currencies(
        self,
        amount: float,
        currencies: list
    ) -> Dict[str, Any]:

        if self.logger:
            self.logger.log_tool_call(
                "CurrencyConverter.compare_currencies",
                {"amount": amount, "currencies_count": len(currencies)},
            )

        conversions = {}

        for currency in currencies:
            try:
                conversions[currency] = self.convert(amount, "USD", currency)
            except ValueError as e:
                if self.logger:
                    self.logger.log_exception(e, f"compare_currencies:{currency}")
                pass

        if not conversions:
            return {"error": "No valid currencies provided"}

        strongest = min(conversions, key=conversions.get)
        weakest = max(conversions, key=conversions.get)

        return {
            "base_amount": amount,
            "base_currency": "USD",
            "conversions": conversions,
            "strongest": strongest,
            "weakest": weakest,
            "last_updated": self.last_updated
        }

    # ------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------
    def _get_supported_list(self) -> str:
        currencies = sorted(self.rates_to_usd.keys())
        return ", ".join(currencies[:10]) + "..." if len(currencies) > 10 else ", ".join(currencies)

    def __repr__(self) -> str:
        return f"CurrencyConverter({len(self.rates_to_usd)} currencies, updated: {self.last_updated})"
