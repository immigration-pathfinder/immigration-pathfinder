# tools/currency_converter.py

from typing import Dict, Any, Optional
from datetime import datetime

from tools.logger import Logger  


class CurrencyConverter:
    """
    Currency converter for normalizing amounts to USD.
    
    Uses static exchange rates suitable for MVP/offline environments.
    For production, can be extended with live FX API integration.
    """
    
    def __init__(self, last_updated: Optional[str] = None):
        """
        Initialize with exchange rates.
        
        Args:
            last_updated: Optional custom update date (default: 2024-11-24)
        """
        self.logger = Logger()  # ✅ لاگر فقط اینجاست
        self.last_updated = last_updated or "2024-11-24"
        
        # Exchange rates: 1 unit of currency ≈ rate USD
        self.rates_to_usd: Dict[str, float] = {
            # Major currencies
            "USD": 1.0,
            "EUR": 1.10,    # 1 EUR ≈ 1.10 USD
            "GBP": 1.27,    # 1 GBP ≈ 1.27 USD
            "CAD": 0.75,    # 1 CAD ≈ 0.75 USD
            "AUD": 0.65,    # 1 AUD ≈ 0.65 USD
            "NZD": 0.60,    # 1 NZD ≈ 0.60 USD
            
            # European currencies
            "CHF": 1.15,    # Swiss Franc
            "SEK": 0.095,   # Swedish Krona
            "NOK": 0.092,   # Norwegian Krone
            "DKK": 0.147,   # Danish Krone
            
            # Asian currencies
            "CNY": 0.14,    # Chinese Yuan
            "JPY": 0.0067,  # Japanese Yen
            "INR": 0.012,   # Indian Rupee
            "SGD": 0.74,    # Singapore Dollar
            "HKD": 0.128,   # Hong Kong Dollar
            "KRW": 0.00076, # South Korean Won
            
            # Middle Eastern currencies
            "AED": 0.27,    # UAE Dirham
            "SAR": 0.27,    # Saudi Riyal
            "ILS": 0.27,    # Israeli Shekel
            "IRR": 0.000020,# Iranian Rial (approximate, highly volatile)
            
            # Latin American currencies
            "BRL": 0.20,    # Brazilian Real
            "MXN": 0.059,   # Mexican Peso
            "ARS": 0.0011,  # Argentine Peso
            
            # Other currencies
            "ZAR": 0.055,   # South African Rand
            "TRY": 0.034,   # Turkish Lira
            "RUB": 0.010,   # Russian Ruble
        }
        
        print(f"[INFO] Currency rates initialized (last updated: {self.last_updated})")
        # ✅ فقط یه لاگ ساده کنار پرینت
        self.logger.log_tool_call(
            "CurrencyConverter.__init__",
            {"last_updated": self.last_updated, "currency_count": len(self.rates_to_usd)},
        )
    
    def convert(
        self,
        amount: float,
        from_curr: str,
        to_curr: str = "USD",
        decimals: int = 2
    ) -> float:
        """
        Convert amount between currencies.
        
        Args:
            amount: Amount to convert
            from_curr: Source currency code (e.g., "EUR")
            to_curr: Target currency code (default: "USD")
            decimals: Number of decimal places (default: 2)
            
        Returns:
            Converted amount rounded to specified decimals
            
        Raises:
            ValueError: If amount is negative or currency is unsupported
        """
        # ✅ فقط لاگ، بدون تغییر منطق
        self.logger.log_tool_call(
            "CurrencyConverter.convert",
            {
                "amount": amount,
                "from_curr": from_curr,
                "to_curr": to_curr,
                "decimals": decimals,
            },
        )

        if amount < 0:
            raise ValueError("Amount must be non-negative.")
        
        if amount == 0:
            return 0.0
        
        # Validate very large amounts
        if amount > 1e12:
            raise ValueError("Amount is unrealistically large (> 1 trillion).")
        
        from_curr = from_curr.upper()
        to_curr = to_curr.upper()
        
        if from_curr not in self.rates_to_usd:
            raise ValueError(
                f"Unsupported source currency: {from_curr}. "
                f"Supported: {self._get_supported_list()}"
            )
        
        if to_curr not in self.rates_to_usd:
            raise ValueError(
                f"Unsupported target currency: {to_curr}. "
                f"Supported: {self._get_supported_list()}"
            )
        
        # Convert: source → USD → target
        amount_in_usd = amount * self.rates_to_usd[from_curr]
        
        if to_curr == "USD":
            target_amount = amount_in_usd
        else:
            target_amount = amount_in_usd / self.rates_to_usd[to_curr]
        
        return round(target_amount, decimals)
    
    def normalize_to_usd(self, amount: float, currency: str) -> float:
        """
        Shortcut to convert amount from any supported currency to USD.
        
        Args:
            amount: Amount to convert
            currency: Source currency code
            
        Returns:
            Amount in USD
        """
        self.logger.log_tool_call(
            "CurrencyConverter.normalize_to_usd",
            {"amount": amount, "currency": currency},
        )
        return self.convert(amount, currency, "USD")
    
    def convert_with_info(
        self,
        amount: float,
        from_curr: str,
        to_curr: str = "USD"
    ) -> Dict[str, Any]:
        """
        Convert and return detailed information.
        
        Args:
            amount: Amount to convert
            from_curr: Source currency
            to_curr: Target currency
            
        Returns:
            {
                "original_amount": float,
                "original_currency": str,
                "converted_amount": float,
                "converted_currency": str,
                "exchange_rate": float,
                "last_updated": str,
                "calculation": str
            }
        """
        self.logger.log_tool_call(
            "CurrencyConverter.convert_with_info",
            {"amount": amount, "from_curr": from_curr, "to_curr": to_curr},
        )

        converted = self.convert(amount, from_curr, to_curr)
        
        from_curr = from_curr.upper()
        to_curr = to_curr.upper()
        
        # Get exchange rate
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
    
    def get_supported_currencies(self) -> Dict[str, float]:
        """
        Return a copy of supported currencies and their rates to USD.
        
        Returns:
            Dictionary of {currency_code: rate_to_usd}
        """
        self.logger.log_tool_call(
            "CurrencyConverter.get_supported_currencies",
            {"count": len(self.rates_to_usd)},
        )
        return self.rates_to_usd.copy()
    
    def get_currency_info(self, currency: str) -> Dict[str, Any]:
        """
        Get detailed information about a currency.
        
        Args:
            currency: Currency code
            
        Returns:
            {
                "code": str,
                "rate_to_usd": float,
                "usd_to_currency": float,
                "supported": bool,
                "last_updated": str
            }
        """
        currency = currency.upper()
        self.logger.log_tool_call(
            "CurrencyConverter.get_currency_info",
            {"currency": currency},
        )
        
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
            "usd_to_currency": round(1 / rate, 6) if rate > 0 else 0,
            "supported": True,
            "last_updated": self.last_updated,
            "example": f"1 {currency} = {rate} USD, 1 USD = {round(1/rate, 2)} {currency}"
        }
    
    def update_rate(self, currency: str, rate: float, source: str = "manual"):
        """
        Update the USD exchange rate for a given currency.
        
        Args:
            currency: Currency code (e.g., "EUR")
            rate: New rate (1 unit of currency ≈ rate USD)
            source: Source of the rate (e.g., "manual", "api")
        """
        currency = currency.upper()
        old_rate = self.rates_to_usd.get(currency, "N/A")
        self.rates_to_usd[currency] = rate
        self.last_updated = datetime.now().strftime("%Y-%m-%d")
        
        print(f"[INFO] Updated {currency} rate: {old_rate} → {rate} (source: {source})")
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
    
    def bulk_convert(
        self,
        amounts: Dict[str, float],
        to_curr: str = "USD"
    ) -> Dict[str, float]:
        """
        Convert multiple amounts from different currencies to target currency.
        
        Args:
            amounts: Dictionary of {currency: amount}
            to_curr: Target currency
            
        Returns:
            Dictionary of {currency: converted_amount}
            
        Example:
            >>> converter.bulk_convert({"EUR": 1000, "GBP": 500, "CAD": 2000})
            {"EUR": 1100.0, "GBP": 635.0, "CAD": 1500.0}
        """
        self.logger.log_tool_call(
            "CurrencyConverter.bulk_convert",
            {"len_amounts": len(amounts), "to_curr": to_curr},
        )
        results = {}
        
        for currency, amount in amounts.items():
            try:
                results[currency] = self.convert(amount, currency, to_curr)
            except ValueError as e:
                results[currency] = f"Error: {e}"
        
        return results
    
    def compare_currencies(
        self,
        amount: float,
        currencies: list
    ) -> Dict[str, Any]:
        """
        Compare how much an amount in USD is worth in different currencies.
        
        Args:
            amount: Amount in USD
            currencies: List of currency codes
            
        Returns:
            {
                "base_amount": float,
                "base_currency": "USD",
                "conversions": {currency: amount},
                "strongest": str,
                "weakest": str
            }
        """
        self.logger.log_tool_call(
            "CurrencyConverter.compare_currencies",
            {"amount": amount, "currencies_count": len(currencies)},
        )

        conversions = {}
        
        for currency in currencies:
            try:
                conversions[currency] = self.convert(amount, "USD", currency)
            except ValueError:
                # مثل قبل، فقط رد می‌شه، لاجیک عوض نشد
                pass
        
        if not conversions:
            return {"error": "No valid currencies provided"}
        
        # Find strongest (least amount) and weakest (most amount)
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
    
    # ============== Internal Methods ==============
    
    def _get_supported_list(self) -> str:
        """Get comma-separated list of supported currencies."""
        currencies = sorted(self.rates_to_usd.keys())
        return ", ".join(currencies[:10]) + "..." if len(currencies) > 10 else ", ".join(currencies)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"CurrencyConverter({len(self.rates_to_usd)} currencies, updated: {self.last_updated})"
