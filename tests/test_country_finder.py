
# tests/test_country_finder_agent.py

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.country_finder_agent import CountryFinderAgent


def test_initialization():
    """Test CountryFinderAgent initialization."""
    print("\n" + "="*70)
    print("TEST 1: Initialization")
    print("="*70)
    
    # Valid initialization
    match_results = [
        {
            "country": "Canada",
            "pathway": "Study",
            "status": "OK",
            "raw_score": 0.85,
            "rule_gaps": {"missing_requirements": []}
        }
    ]
    
    user_profile = {
        "age": 27,
        "ielts": 6.5,
        "funds_usd": 22000
    }
    
    try:
        finder = CountryFinderAgent(match_results, user_profile)
        print("✅ Valid initialization successful")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        raise
    
    # Test empty match_results
    try:
        finder = CountryFinderAgent([], user_profile)
        print("❌ Should have raised ValueError for empty match_results")
        assert False
    except ValueError as e:
        print(f"✅ Empty match_results rejected: {e}")
    
    # Test empty profile
    try:
        finder = CountryFinderAgent(match_results, {})
        print("❌ Should have raised ValueError for empty profile")
        assert False
    except ValueError as e:
        print(f"✅ Empty profile rejected: {e}")
    
    print()


def test_eligibility_scoring():
    """Test eligibility scoring based on match status."""
    print("="*70)
    print("TEST 2: Eligibility Scoring")
    print("="*70)
    
    user_profile = {"age": 27, "ielts": 6.5}
    
    # Test OK status
    match_ok = {
        "country": "Canada",
        "status": "OK",
        "raw_score": 0.90,
        "rule_gaps": {}
    }
    
    finder = CountryFinderAgent([match_ok], user_profile)
    score = finder._score_eligibility(match_ok)
    assert score == 0.90, f"Expected 0.90, got {score}"
    print(f"✅ OK status: raw_score 0.90 → {score}")
    
    # Test Borderline status
    match_borderline = {
        "country": "Germany",
        "status": "Borderline",
        "raw_score": 0.70,
        "rule_gaps": {}
    }
    
    finder = CountryFinderAgent([match_borderline], user_profile)
    score = finder._score_eligibility(match_borderline)
    assert abs(score - 0.56) < 0.01, f"Expected ~0.56, got {score}"  # 0.70 * 0.8
    print(f"✅ Borderline status: raw_score 0.70 × 0.8 → {score}")
    
    # Test High Risk status
    match_risk = {
        "country": "USA",
        "status": "High Risk",
        "raw_score": 0.50,
        "rule_gaps": {}
    }
    
    finder = CountryFinderAgent([match_risk], user_profile)
    score = finder._score_eligibility(match_risk)
    assert score == 0.25, f"Expected 0.25, got {score}"  # 0.50 * 0.5
    print(f"✅ High Risk status: raw_score 0.50 × 0.5 → {score}")
    
    print()


def test_language_alignment():
    """Test language alignment scoring."""
    print("="*70)
    print("TEST 3: Language Alignment Scoring")
    print("="*70)
    
    match_result = {
        "country": "Canada",
        "status": "OK",
        "raw_score": 0.85,
        "rule_gaps": {}
    }
    
    # Test high IELTS
    profile_high_ielts = {
        "age": 27,
        "ielts": 7.5,
        "german_level": "none",
        "french_level": "none"
    }
    
    finder = CountryFinderAgent([match_result], profile_high_ielts)
    score = finder._score_language_alignment("Canada")
    assert score >= 0.5, f"High IELTS should score >= 0.5, got {score}"
    print(f"✅ IELTS 7.5 for Canada (English): {score}")
    
    # Test moderate IELTS
    profile_moderate_ielts = {
        "age": 27,
        "ielts": 6.0,
        "german_level": "none",
        "french_level": "none"
    }
    
    finder = CountryFinderAgent([match_result], profile_moderate_ielts)
    score = finder._score_language_alignment("Canada")
    assert 0.3 <= score <= 0.5, f"Moderate IELTS should score 0.3-0.5, got {score}"
    print(f"✅ IELTS 6.0 for Canada: {score}")
    
    # Test German proficiency for Germany
    profile_german = {
        "age": 27,
        "ielts": 6.0,
        "german_level": "B2",
        "french_level": "none"
    }
    
    finder = CountryFinderAgent([match_result], profile_german)
    score = finder._score_language_alignment("Germany")
    assert score >= 0.7, f"IELTS 6.0 + German B2 should score >= 0.7, got {score}"
    print(f"✅ IELTS 6.0 + German B2 for Germany: {score}")
    
    # Test French for Canada
    profile_french = {
        "age": 27,
        "ielts": 6.5,
        "german_level": "none",
        "french_level": "B1"
    }
    
    finder = CountryFinderAgent([match_result], profile_french)
    score = finder._score_language_alignment("Canada")
    assert score >= 0.8, f"IELTS 6.5 + French B1 should score >= 0.8, got {score}"
    print(f"✅ IELTS 6.5 + French B1 for Canada: {score}")
    
    print()


def test_financial_capacity():
    """Test financial capacity scoring."""
    print("="*70)
    print("TEST 4: Financial Capacity Scoring")
    print("="*70)
    
    user_profile = {"age": 27, "funds_usd": 18000}
    
    # Test sufficient funds (no gaps)
    match_sufficient = {
        "country": "Germany",
        "status": "OK",
        "raw_score": 0.90,
        "rule_gaps": {
            "missing_requirements": []  # No funds issue
        }
    }
    
    finder = CountryFinderAgent([match_sufficient], user_profile)
    score = finder._score_financial_capacity(match_sufficient)
    assert score == 1.0, f"Sufficient funds should score 1.0, got {score}"
    print(f"✅ Sufficient funds (no gaps): {score}")
    
    # Test funds gap (mentioned in gaps)
    match_gap = {
        "country": "USA",
        "status": "Borderline",
        "raw_score": 0.65,
        "rule_gaps": {
            "missing_requirements": [
                "Insufficient funds (need $35000, have $18000)"
            ]
        }
    }
    
    finder = CountryFinderAgent([match_gap], user_profile)
    score = finder._score_financial_capacity(match_gap)
    assert 0.5 <= score <= 0.8, f"Funds gap should score 0.5-0.8, got {score}"
    print(f"✅ Funds gap (raw_score 0.65): {score}")
    
    print()


def test_calculate_final_score():
    """Test final score calculation with all factors."""
    print("="*70)
    print("TEST 5: Final Score Calculation")
    print("="*70)
    
    # Strong candidate for Germany
    match_result = {
        "country": "Germany",
        "pathway": "Study",
        "status": "OK",
        "raw_score": 0.90,
        "rule_gaps": {
            "missing_requirements": []
        }
    }
    
    user_profile = {
        "age": 27,
        "ielts": 6.5,
        "german_level": "B2",
        "french_level": "none",
        "funds_usd": 20000
    }
    
    finder = CountryFinderAgent([match_result], user_profile)
    final_score = finder._calculate_final_score(match_result)
    
    print(f"  Country: Germany")
    print(f"  Status: OK (raw_score: 0.90)")
    print(f"  IELTS: 6.5, German: B2")
    print(f"  Funds: $20,000")
    print(f"  Final Score: {final_score}/100")
    
    assert 70 <= final_score <= 100, f"Strong candidate should score 70-100, got {final_score}"
    print(f"✅ Final score in expected range")
    
    # Weak candidate for USA
    match_result_usa = {
        "country": "USA",
        "pathway": "Study",
        "status": "High Risk",
        "raw_score": 0.40,
        "rule_gaps": {
            "missing_requirements": [
                "Insufficient funds (need $35000, have $15000)"
            ]
        }
    }
    
    user_profile_weak = {
        "age": 27,
        "ielts": 5.5,
        "german_level": "none",
        "french_level": "none",
        "funds_usd": 15000
    }
    
    finder_usa = CountryFinderAgent([match_result_usa], user_profile_weak)
    final_score_usa = finder_usa._calculate_final_score(match_result_usa)
    
    print(f"\n  Country: USA")
    print(f"  Status: High Risk (raw_score: 0.40)")
    print(f"  IELTS: 5.5, Funds: $15,000")
    print(f"  Final Score: {final_score_usa}/100")
    
    assert final_score_usa < 60, f"Weak candidate should score < 60, got {final_score_usa}"
    print(f"✅ Weak candidate scored correctly")
    
    print()


def test_rank_countries():
    """Test complete ranking of multiple countries."""
    print("="*70)
    print("TEST 6: Rank Countries (Complete Workflow)")
    print("="*70)
    
    # Multiple countries with different statuses
    match_results = [
        {
            "country": "Germany",
            "pathway": "Study",
            "status": "OK",
            "raw_score": 0.90,
            "rule_gaps": {"missing_requirements": []}
        },
        {
            "country": "Canada",
            "pathway": "Study",
            "status": "Borderline",
            "raw_score": 0.70,
            "rule_gaps": {
                "missing_requirements": ["Funds slightly below recommended"]
            }
        },
        {
            "country": "USA",
            "pathway": "Study",
            "status": "High Risk",
            "raw_score": 0.40,
            "rule_gaps": {
                "missing_requirements": [
                    "Insufficient funds (need $35000, have $18000)",
                    "IELTS below recommended"
                ]
            }
        },
        {
            "country": "Netherlands",
            "pathway": "Study",
            "status": "OK",
            "raw_score": 0.85,
            "rule_gaps": {"missing_requirements": []}
        }
    ]
    
    user_profile = {
        "age": 27,
        "ielts": 6.5,
        "german_level": "B1",
        "french_level": "none",
        "funds_usd": 18000,
        "work_experience_years": 3
    }
    
    finder = CountryFinderAgent(match_results, user_profile)
    ranking = finder.rank_countries()
    
    print("\n📊 Ranking Results:")
    print("-" * 70)
    
    # Check structure
    assert "best_options" in ranking
    assert "acceptable" in ranking
    assert "not_recommended" in ranking
    assert "scores" in ranking
    assert "detailed_breakdown" in ranking
    print("✅ All required keys present in ranking")
    
    # Check scores
    scores = ranking["scores"]
    print(f"\n📈 Scores:")
    for country, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        print(f"  {country}: {score}/100")
    
    assert len(scores) == 4, f"Expected 4 countries, got {len(scores)}"
    print(f"✅ All 4 countries scored")
    
    # Check classifications
    best = ranking["best_options"]
    acceptable = ranking["acceptable"]
    not_recommended = ranking["not_recommended"]
    
    print(f"\n🏆 Best Options ({len(best)}):")
    for option in best:
        print(f"  • {option['country']}: {option['score']}/100")
        print(f"    Reason: {option['reason'][:80]}...")
    
    print(f"\n⚠️  Acceptable ({len(acceptable)}):")
    for option in acceptable:
        print(f"  • {option['country']}: {option['score']}/100")
        print(f"    Reason: {option['reason'][:80]}...")
    
    print(f"\n❌ Not Recommended ({len(not_recommended)}):")
    for country in not_recommended:
        print(f"  • {country}")
    
    # Verify classifications
    total_countries = len(best) + len(acceptable) + len(not_recommended)
    assert total_countries == 4, f"Expected 4 total, got {total_countries}"
    print(f"\n✅ All countries classified correctly")
    
    # Check detailed breakdown
    breakdown = ranking["detailed_breakdown"]
    assert len(breakdown) == 4, f"Expected 4 breakdowns, got {len(breakdown)}"
    
    print(f"\n🔍 Detailed Breakdown (First Country):")
    first = breakdown[0]
    print(f"  Country: {first['country']}")
    print(f"  Final Score: {first['final_score']}/100")
    print(f"  Eligibility: {first['eligibility_status']} ({first['eligibility_raw_score']})")
    print(f"  Language Score: {first['language_score']}/100")
    print(f"  Financial Score: {first['financial_score']}/100")
    print(f"  Visa Difficulty: {first['visa_difficulty']}/100")
    print(f"  Quality of Life: {first['quality_of_life']}/100")
    print(f"  Cost of Living: {first['cost_of_living']}/100")
    print(f"  Job Market: {first['job_market']}/100")
    
    print(f"\n✅ Detailed breakdown provided")
    
    print()


def test_top_recommendation():
    """Test getting single top recommendation."""
    print("="*70)
    print("TEST 7: Top Recommendation")
    print("="*70)
    
    match_results = [
        {
            "country": "Germany",
            "status": "OK",
            "raw_score": 0.90,
            "rule_gaps": {"missing_requirements": []}
        },
        {
            "country": "Canada",
            "status": "Borderline",
            "raw_score": 0.70,
            "rule_gaps": {"missing_requirements": ["Minor gap"]}
        }
    ]
    
    user_profile = {
        "age": 27,
        "ielts": 6.5,
        "german_level": "B2",
        "funds_usd": 20000
    }
    
    finder = CountryFinderAgent(match_results, user_profile)
    top = finder.get_top_recommendation()
    
    assert top is not None, "Should return a recommendation"
    print(f"✅ Top recommendation: {top}")
    
    # Verify it's the highest scoring
    ranking = finder.rank_countries()
    if ranking["best_options"]:
        expected_top = ranking["best_options"][0]["country"]
        assert top == expected_top, f"Expected {expected_top}, got {top}"
        print(f"✅ Matches highest scored country")
    
    print()


def test_edge_cases():
    """Test edge cases and error handling."""
    print("="*70)
    print("TEST 8: Edge Cases")
    print("="*70)
    
    # Test with no language skills
    match_result = {
        "country": "Canada",
        "status": "OK",
        "raw_score": 0.80,
        "rule_gaps": {"missing_requirements": []}
    }
    
    profile_no_language = {
        "age": 27,
        "ielts": 0,
        "german_level": "none",
        "french_level": "none",
        "funds_usd": 25000
    }
    
    try:
        finder = CountryFinderAgent([match_result], profile_no_language)
        score = finder._score_language_alignment("Canada")
        print(f"✅ No language skills handled: score = {score}")
    except Exception as e:
        print(f"❌ Failed with no language: {e}")
        raise
    
    # Test with missing profile fields
    profile_minimal = {
        "age": 27
    }
    
    try:
        finder = CountryFinderAgent([match_result], profile_minimal)
        final_score = finder._calculate_final_score(match_result)
        print(f"✅ Minimal profile handled: score = {final_score}")
    except Exception as e:
        print(f"❌ Failed with minimal profile: {e}")
        raise
    
    # Test with unknown country
    match_unknown = {
        "country": "Unknown",
        "status": "OK",
        "raw_score": 0.80,
        "rule_gaps": {"missing_requirements": []}
    }
    
    try:
        finder = CountryFinderAgent([match_unknown], profile_minimal)
        score = finder._calculate_final_score(match_unknown)
        print(f"✅ Unknown country handled with defaults: score = {score}")
    except Exception as e:
        print(f"❌ Failed with unknown country: {e}")
        raise
    
    print()


def run_all_tests():
    """Run all CountryFinderAgent tests."""
    print("\n" + "="*70)
    print("🚀 STARTING COUNTRY FINDER AGENT TESTS")
    print("="*70)
    
    tests = [
        ("Initialization", test_initialization),
        ("Eligibility Scoring", test_eligibility_scoring),
        ("Language Alignment", test_language_alignment),
        ("Financial Capacity", test_financial_capacity),
        ("Final Score Calculation", test_calculate_final_score),
        ("Rank Countries", test_rank_countries),
        ("Top Recommendation", test_top_recommendation),
        ("Edge Cases", test_edge_cases),
    ]
    
    passed = 0
    failed = 0
    errors = []
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            failed += 1
            errors.append(f"{name}: {e}")
            print(f"\n❌ {name} FAILED: {e}\n")
        except Exception as e:
            failed += 1
            errors.append(f"{name}: {e}")
            print(f"\n❌ {name} ERROR: {e}\n")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    print(f"✅ Passed:  {passed}/{len(tests)}")
    print(f"❌ Failed:  {failed}/{len(tests)}")
    
    if errors:
        print("\n❌ Failed Tests:")
        for error in errors:
            print(f"  • {error}")
    
    print("="*70)
    
    if failed > 0:
        print("\n❌ SOME TESTS FAILED")
        exit(1)
    else:
        print("\n✅ ALL TESTS PASSED! 🎉")


if __name__ == "__main__":
    run_all_tests()
