# tests/test_tools_off_kaggle.py
"""
Immigration Pathfinder Tools - Kaggle Test Suite

This test suite is designed to work in Kaggle Notebook environment
with automatic path detection and graceful handling of missing dependencies.
"""

import sys
from pathlib import Path

print("=" * 70)
print("🔧 SETUP: Configuring Kaggle Environment")
print("=" * 70)

# ============================================================
# PATH SETUP FOR KAGGLE
# ============================================================

# Try multiple common paths
possible_paths = [
    Path("/kaggle/input/NAME/tools"),
    Path("/kaggle/input/NAME/tools"),
    
    # Working directory
    Path("/kaggle/input/NAME/tools"),
    
    # Current directory
    Path("tools"),
]


PROJECT_ROOT = None
for path in possible_paths:
    if path.exists():
        PROJECT_ROOT = path
        sys.path.insert(0, str(path.parent))
        print(f"✅ Found tools at: {path}")
        break

if PROJECT_ROOT is None:
    print("\n❌ ERROR: Could not find tools directory!")
    print("\nSearched paths:")
    for p in possible_paths:
        print(f"  ❌ {p}")
    print("\n💡 Solutions:")
    print("  1. Upload 'tools' folder as a Kaggle Dataset")
    print("  2. Copy tools to /kaggle/working/")
    print("  3. Adjust path in this script")
    sys.exit(1)

# ============================================================
# IMPORTS WITH ERROR HANDLING
# ============================================================

try:
    from tools.search_tool import SearchTool
    from tools.funds_calculator import FundsGapCalculator
    from tools.currency_converter import CurrencyConverter
    print("✅ All tools imported successfully\n")
except ImportError as e:
    print(f"\n❌ Import failed: {e}")
    print("\n💡 Make sure tools/__init__.py exists:")
    print("   - tools/__init__.py")
    print("   - tools/search_tool.py")
    print("   - tools/funds_calculator.py")
    print("   - tools/currency_converter.py")
    sys.exit(1)


# ============================================================
# TEST 1 — OFFLINE MODE (MOCK)
# ============================================================

def test_search_tool_mock():
    """Test SearchTool in mock/offline mode."""
    print("=" * 70)
    print("TEST 1: SearchTool (Mock/Offline Mode)")
    print("=" * 70)
    
    try:
        tool = SearchTool()  # Mock mode
        
        # Basic search
        results = tool.search_immigration("student visa requirements", "Canada")
        assert len(results) > 0, "No results returned"
        assert results[0]["source"] == "mock_search", "Wrong source type"
        print(f"✅ Mock search: {len(results)} results")

        # Visa difficulty
        difficulty = tool.search_visa_difficulty("Canada", "Study")
        assert difficulty["country"] == "Canada", "Wrong country"
        print(f"✅ Visa difficulty: {difficulty['difficulty']}")

        # Job market
        job = tool.search_job_market("Germany", "Engineering")
        assert job["country"] == "Germany", "Wrong country"
        print(f"✅ Job market: {job['outlook']}")

        # History
        history = tool.get_search_history()
        assert len(history) == 3, f"Expected 3 entries, got {len(history)}"
        print(f"✅ History: {len(history)} entries")
        
        # Stats
        stats = tool.get_stats()
        assert stats["mode"] == "mock", "Wrong mode"
        print(f"✅ Stats: {stats['mode']} mode\n")
        
    except Exception as e:
        print(f"❌ Test failed: {e}\n")
        raise


# ============================================================
# TEST 2 — ONLINE MODE (WITH GEMINI)
# ============================================================

def test_search_tool_gemini():
    """Test SearchTool with Gemini API (if available)."""
    print("=" * 70)
    print("TEST 2: SearchTool with Gemini (Online Mode)")
    print("=" * 70)

    # Check if we're in Kaggle
    try:
        from kaggle_secrets import UserSecretsClient
        import google.generativeai as genai
    except ImportError as e:
        print(f"⏭️  SKIPPED: Not in Kaggle environment ({e})\n")
        return

    # Try to load API key
    try:
        api_key = UserSecretsClient().get_secret("GOOGLE_API_KEY")
        if not api_key:
            print("⏭️  SKIPPED: GOOGLE_API_KEY not configured in Kaggle Secrets\n")
            return
    except Exception as e:
        print(f"⏭️  SKIPPED: Cannot access API key ({e})\n")
        return

    # Configure Gemini
    try:
        genai.configure(api_key=api_key)
        print("✅ Gemini API configured")
    except Exception as e:
        print(f"⏭️  SKIPPED: Gemini configuration failed ({e})\n")
        return

    # Find available model
    try:
        models = [
            m.name for m in genai.list_models()
            if "generateContent" in m.supported_generation_methods
        ]
        
        if not models:
            print("⏭️  SKIPPED: No Gemini models available\n")
            return

        # Prefer flash models (faster, cheaper)
        model_name = None
        for priority in ["flash", "2.0", "gemini"]:
            for m in models:
                if priority in m.lower() and "thinking" not in m.lower():
                    model_name = m
                    break
            if model_name:
                break
        
        if not model_name:
            model_name = models[0]

        model = genai.GenerativeModel(model_name)
        print(f"✅ Using model: {model_name}")

    except Exception as e:
        print(f"⏭️  SKIPPED: Model selection failed ({e})\n")
        return

    # Create Gemini-powered search function
    def gemini_search(query: str, num_results: int = 3):
        """Gemini-based search function."""
        prompt = f"""
Provide a brief summary (2-3 bullet points, max 200 words) about this immigration query.
Use clear, factual language. Non-legal advice only.

Query: {query}

Format your response as bullet points starting with •
"""
        try:
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.3, "max_output_tokens": 500}
            )
            text = (response.text or "").strip()
            
            return [{
                "title": f"Gemini AI Summary: {query[:50]}...",
                "url": "https://ai.google.dev/gemini-api",
                "snippet": text[:400] if text else "No response generated",
                "source": "gemini_search"
            }]
        except Exception as e:
            print(f"⚠️  Gemini search error: {e}")
            return []

    # Test with Gemini
    try:
        tool = SearchTool(search_func=gemini_search)
        
        results = tool.search_immigration(
            "student visa requirements Canada 2024",
            country="Canada",
            pathway="Study",
            max_results=2
        )
        
        assert isinstance(results, list), "Results should be a list"
        assert len(results) > 0, "No results returned"
        
        print(f"✅ Gemini search: {len(results)} results")
        
        if results:
            print(f"   Title: {results[0]['title'][:60]}...")
            print(f"   Preview: {results[0]['snippet'][:100]}...")
        
        print()
        
    except Exception as e:
        print(f"❌ Gemini test failed: {e}\n")
        raise


# ============================================================
# TEST 3 — FUNDS GAP CALCULATOR
# ============================================================

def test_funds_calculator():
    """Test FundsGapCalculator."""
    print("=" * 70)
    print("TEST 3: FundsGapCalculator")
    print("=" * 70)

    try:
        calc = FundsGapCalculator()

        # Test all statuses
        assert calc.calculate_gap(25000, 22000)["status"] == "OK"
        assert calc.calculate_gap(18000, 22000)["status"] == "NEAR"
        assert calc.calculate_gap(12000, 22000)["status"] == "UNDERFUNDED"
        assert calc.calculate_gap(5000, 22000)["status"] == "CRITICAL"
        print("✅ All status levels work correctly")

        # Test coverage_percent
        result = calc.calculate_gap(18000, 22000)
        assert "coverage_percent" in result, "Missing coverage_percent"
        assert 80 <= result["coverage_percent"] < 85, "Wrong coverage"
        print(f"✅ Coverage percent: {result['coverage_percent']}%")

        # Test monthly needs
        monthly = calc.calculate_monthly_needs("Germany", 12)
        assert monthly["total_cost"] > 0, "Invalid total cost"
        assert monthly["year"] == 2024, "Wrong year"
        print(f"✅ Monthly needs: ${monthly['monthly_cost']}/month")

        # Test total needs
        total = calc.calculate_total_needs("Canada", "Study", 12)
        assert total["living_cost"] > 0, "Invalid living cost"
        assert total["tuition_cost"] > 0, "Invalid tuition cost"
        assert total["total_needed"] > 0, "Invalid total"
        print(f"✅ Total needs: ${total['total_needed']:,.0f}")

        # Test compare affordability
        comparison = calc.compare_affordability(
            20000,
            ["Germany", "Canada", "USA"],
            "Study",
            12
        )
        assert len(comparison["countries"]) == 3, "Wrong country count"
        assert comparison["most_affordable"] is not None, "No most affordable"
        print(f"✅ Comparison: {comparison['most_affordable']} is most affordable")

        # Test savings plan
        savings = calc.get_savings_plan(15000, 20000, 1000)
        assert savings["gap"] == 5000, "Wrong gap"
        assert savings["months_needed"] in [5, 6], "Wrong months"
        assert savings["feasible"] == True, "Should be feasible"
        print(f"✅ Savings plan: {savings['months_needed']} months\n")
        
    except Exception as e:
        print(f"❌ Test failed: {e}\n")
        raise


# ============================================================
# TEST 4 — CURRENCY CONVERTER
# ============================================================

def test_currency_converter():
    """Test CurrencyConverter."""
    print("=" * 70)
    print("TEST 4: CurrencyConverter")
    print("=" * 70)

    try:
        converter = CurrencyConverter()

        # Test basic conversions
        assert converter.convert(1000, "EUR", "USD") == 1100.0
        assert converter.convert(1000, "CAD", "USD") == 750.0
        print("✅ EUR/CAD to USD conversions correct")

        # Test normalize
        assert converter.normalize_to_usd(100, "EUR") == 110.0
        print("✅ Normalize to USD works")

        # Test currency info
        info = converter.convert_with_info(1000, "EUR", "USD")
        assert "exchange_rate" in info, "Missing exchange_rate"
        assert info["converted_amount"] == 1100.0, "Wrong amount"
        print(f"✅ Detailed info: {info['calculation']}")

        # Test supported currencies
        currencies = converter.get_supported_currencies()
        assert len(currencies) >= 25, f"Expected 25+ currencies, got {len(currencies)}"
        assert "USD" in currencies and "EUR" in currencies
        print(f"✅ Supports {len(currencies)} currencies")

        # Test bulk convert
        bulk = converter.bulk_convert({"EUR": 1000, "CAD": 2000})
        assert bulk["EUR"] == 1100.0, "Wrong EUR conversion"
        assert bulk["CAD"] == 1500.0, "Wrong CAD conversion"
        print("✅ Bulk conversion works")

        # Test error handling
        try:
            converter.convert(100, "INVALID", "USD")
            assert False, "Should raise error"
        except ValueError:
            print("✅ Invalid currency rejected\n")
            
    except Exception as e:
        print(f"❌ Test failed: {e}\n")
        raise


# ============================================================
# TEST 5 — INTEGRATION
# ============================================================

def test_integration():
    """Test all tools working together."""
    print("=" * 70)
    print("TEST 5: Integration - Complete Workflow")
    print("=" * 70)

    try:
        converter = CurrencyConverter()
        calc = FundsGapCalculator()
        search = SearchTool()

        print("\n📋 Scenario: Iranian student, 20,000 EUR, wants to study in Canada\n")

        # Step 1: Convert currency
        funds_eur = 20000
        funds_usd = converter.normalize_to_usd(funds_eur, "EUR")
        assert funds_usd == 22000.0, f"Expected 22000, got {funds_usd}"
        print(f"  ✅ Step 1: {funds_eur:,} EUR = ${funds_usd:,.0f} USD")

        # Step 2: Calculate Canada needs
        needs = calc.calculate_total_needs("Canada", "Study", 12)
        print(f"  ✅ Step 2: Canada needs ${needs['total_needed']:,.0f}")

        # Step 3: Check affordability
        gap = calc.calculate_gap(funds_usd, needs['total_needed'])
        print(f"  ✅ Step 3: Status {gap['status']}, Coverage {gap['coverage_percent']}%")

        # Step 4: Compare countries
        comparison = calc.compare_affordability(
            funds_usd,
            ["Canada", "Germany", "USA"],
            "Study",
            12
        )
        print(f"  ✅ Step 4: Most affordable is {comparison['most_affordable']}")

        # Step 5: Search info
        results = search.search_immigration("visa", "Canada", "Study")
        assert len(results) > 0, "No search results"
        print(f"  ✅ Step 5: Found {len(results)} search results")

        print("\n✅ Integration test passed!\n")
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}\n")
        raise


# ============================================================
# TEST 6 — PERFORMANCE
# ============================================================

def test_performance():
    """Test performance with many operations."""
    print("=" * 70)
    print("TEST 6: Performance Test")
    print("=" * 70)
    
    import time
    
    try:
        converter = CurrencyConverter()
        calc = FundsGapCalculator()
        search = SearchTool()
        
        start = time.time()
        
        # 100 conversions
        for i in range(100):
            converter.convert(1000 + i, "EUR", "USD")
        
        # 100 gap calculations
        for i in range(100):
            calc.calculate_gap(15000 + i*100, 20000)
        
        # 10 searches
        for i in range(10):
            search.search_immigration(f"visa {i}", "Canada")
        
        elapsed = time.time() - start
        
        print(f"  ✅ 210 operations in {elapsed:.3f} seconds")
        print(f"  ✅ Average: {elapsed/210*1000:.2f}ms per operation")
        
        assert elapsed < 3.0, "Performance too slow"
        print("✅ Performance test passed\n")
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}\n")
        raise


# ============================================================
# RUN ALL TESTS
# ============================================================

def run_all_tests():
    """Run all tests with proper error handling."""
    print("\n" + "=" * 70)
    print("🚀 STARTING KAGGLE TOOLS TESTS")
    print("=" * 70 + "\n")

    tests = [
        ("Search Tool (Mock)", test_search_tool_mock),
        ("Search Tool (Gemini)", test_search_tool_gemini),
        ("Funds Calculator", test_funds_calculator),
        ("Currency Converter", test_currency_converter),
        ("Integration", test_integration),
        ("Performance", test_performance),
    ]

    passed = 0
    failed = 0
    skipped = 0
    errors = []

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except SystemExit:
            # Test was skipped gracefully
            skipped += 1
        except Exception as e:
            failed += 1
            error_msg = f"{name}: {str(e)[:100]}"
            errors.append(error_msg)
            print(f"❌ {name} FAILED")
            
            # Print traceback for debugging
            import traceback
            print(traceback.format_exc())

    # Summary
    print("=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Passed:  {passed}/{len(tests)}")
    print(f"⏭️  Skipped: {skipped}/{len(tests)}")
    print(f"❌ Failed:  {failed}/{len(tests)}")
    
    if errors:
        print("\n❌ Failed Tests:")
        for error in errors:
            print(f"  • {error}")
    
    print("=" * 70)
    
    if failed > 0:
        print("\n❌ SOME TESTS FAILED")
        print("💡 Check error messages above for details")
    elif passed == len(tests):
        print("\n✅ ALL TESTS PASSED! 🎉")
    else:
        print(f"\n⚠️  {passed} PASSED, {skipped} SKIPPED")


# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
