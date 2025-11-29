
"""
Immigration Pathfinder - Multi-Agent System
Main entry point for the application
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import ها در داخل توابع انجام می‌شود تا از خطای circular import جلوگیری شود


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_colored(text: str, color: str = Colors.ENDC):
    """Print colored text"""
    print(f"{color}{text}{Colors.ENDC}")


def print_banner():
    """Print application banner"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}╔═══════════════════════════════════════════════════════════╗
║        Immigration Pathfinder - Multi-Agent System       ║
║                                                           ║
║     Find your immigration path with AI assistance        ║
╚═══════════════════════════════════════════════════════════╝{Colors.ENDC}
    """
    print(banner)


def get_user_input():
    """Get user information interactively"""
    print("\n=== User Profile Setup ===\n")
    
    # Age
    while True:
        try:
            age = int(input("Enter your age: "))
            if 0 <= age <= 100:
                break
            print("Please enter a valid age between 0 and 100")
        except ValueError:
            print("Please enter a valid number")
    
    # Citizenship
    citizenship = input("Enter your citizenship/nationality: ").strip()
    
    # Marital Status
    print("\nMarital Status options:")
    print("1. Single")
    print("2. Married")
    print("3. Divorced")
    print("4. Widowed")
    
    marital_options = {
        "1": "single",
        "2": "married",
        "3": "divorced",
        "4": "widowed"
    }
    
    while True:
        choice = input("Select marital status (1-4): ").strip()
        if choice in marital_options:
            marital_status = marital_options[choice]
            break
        print("Please select a valid option (1-4)")
    
    # Create user profile
    user_profile = {
        "age": age,
        "citizenship": citizenship,
        "marital_status": marital_status
    }
    
    return user_profile


def save_results_to_file(result: dict, filename: str = None):
    """Save results to JSON file"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"immigration_result_{timestamp}.json"
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    filepath = output_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print_colored(f"\n💾 Results saved to: {filepath}", Colors.GREEN)
    return filepath


def print_summary_table(result: dict):
    """Print a nice summary table of top countries"""
    if "ranking" not in result or "acceptable" not in result["ranking"]:
        return
    
    acceptable = result["ranking"]["acceptable"][:5]  # Top 5
    
    print_colored("\n📊 TOP 5 COUNTRIES SUMMARY", Colors.BOLD + Colors.CYAN)
    print("─" * 70)
    print(f"{'Rank':<6} {'Country':<20} {'Score':<10} {'Status':<15}")
    print("─" * 70)
    
    for idx, country_info in enumerate(acceptable, 1):
        country = country_info["country"]
        score = country_info["score"]
        
        # Color based on score
        if score >= 75:
            color = Colors.GREEN
        elif score >= 65:
            color = Colors.YELLOW
        else:
            color = Colors.RED
        
        status = "✅ Excellent" if score >= 75 else "⚠️  Good" if score >= 65 else "❌ Fair"
        
        print(f"{color}{idx:<6} {country:<20} {score:<10.2f} {status:<15}{Colors.ENDC}")
    
    print("─" * 70)


def interactive_mode():
    """Run the application in interactive mode"""
    print_banner()
    print_colored("🎯 INTERACTIVE MODE", Colors.BOLD + Colors.CYAN)
    print_colored("━" * 60, Colors.CYAN)
    
    # Import here to avoid circular imports
    from memory.session_service import SessionService
    from agents.orchestrator import Orchestrator
    
    # Initialize session service
    session_service = SessionService()
    
    # Get user profile
    user_profile = get_user_input()
    
    print_colored("\n" + "═"*60, Colors.CYAN)
    print_colored("📋 USER PROFILE SUMMARY:", Colors.BOLD + Colors.BLUE)
    print_colored("═"*60, Colors.CYAN)
    print(json.dumps(user_profile, indent=2, ensure_ascii=False))
    print_colored("═"*60 + "\n", Colors.CYAN)
    
    # Initialize orchestrator
    print_colored("⚙️  Initializing AI agents...", Colors.YELLOW)
    orchestrator = Orchestrator(session_service)
    
    # Process user query
    print_colored("\n🔍 IMMIGRATION PATH ANALYSIS", Colors.BOLD + Colors.CYAN)
    print_colored("━" * 60, Colors.CYAN)
    query = input(f"{Colors.BOLD}What would you like to know about immigration? (or 'quit' to exit):{Colors.ENDC} ").strip()
    
    if query.lower() in ['quit', 'exit', 'q']:
        print_colored("\n👋 Thank you for using Immigration Pathfinder!", Colors.GREEN)
        return
    
    # Run orchestration with timing
    print_colored("\n⏳ Processing your request...", Colors.YELLOW)
    print_colored("This may take a moment as agents analyze your profile...\n", Colors.YELLOW)
    
    start_time = time.time()
    
    try:
        result = orchestrator.process(user_profile, query)
        
        elapsed_time = time.time() - start_time
        
        # نمایش توضیحات به صورت زیبا
        if "explanation" in result:
            print_colored("\n" + "═"*60, Colors.CYAN)
            print_colored("📄 IMMIGRATION RECOMMENDATION", Colors.BOLD + Colors.GREEN)
            print_colored("═"*60 + "\n", Colors.CYAN)
            print(result["explanation"])
        
        # نمایش جدول خلاصه
        print_summary_table(result)
        
        # نمایش زمان اجرا
        print_colored(f"\n⏱️  Total processing time: {elapsed_time:.2f} seconds", Colors.BLUE)
        
        # پرسش برای ذخیره نتایج
        save_option = input(f"\n{Colors.BOLD}💾 Save results to file? (y/n):{Colors.ENDC} ").strip().lower()
        if save_option in ['y', 'yes']:
            save_results_to_file(result)
        
        # نمایش جزئیات تکنیکی (اختیاری)
        show_details = input(f"\n{Colors.BOLD}🔧 Show technical details? (y/n):{Colors.ENDC} ").strip().lower()
        if show_details in ['y', 'yes']:
            print_colored("\n" + "═"*60, Colors.CYAN)
            print_colored("📊 TECHNICAL DETAILS", Colors.BOLD + Colors.BLUE)
            print_colored("═"*60, Colors.CYAN)
            
            # حذف explanation از JSON برای جلوگیری از تکرار
            result_copy = result.copy()
            result_copy.pop("explanation", None)
            print(json.dumps(result_copy, indent=2, ensure_ascii=False))
            print_colored("═"*60 + "\n", Colors.CYAN)
        
    except Exception as e:
        print_colored(f"\n❌ Error: {str(e)}", Colors.RED)
        print_colored("Please try again or check your configuration.\n", Colors.YELLOW)


def demo_mode():
    """Run a quick demo with sample data"""
    print_banner()
    print_colored("🎬 DEMO MODE", Colors.BOLD + Colors.CYAN)
    print_colored("━" * 60 + "\n", Colors.CYAN)
    
    # Import here to avoid circular imports
    from memory.session_service import SessionService
    from agents.orchestrator import Orchestrator
    
    # Sample user profile
    sample_profile = {
        "age": 30,
        "citizenship": "India",
        "marital_status": "single"
    }
    
    print("Using sample profile:")
    print(json.dumps(sample_profile, indent=2))
    print()
    
    # Initialize components
    session_service = SessionService()
    orchestrator = Orchestrator(session_service)
    
    # Sample query
    query = "What are my best immigration options for skilled work?"
    print(f"Query: {query}\n")
    
    print("Processing...")
    try:
        result = orchestrator.process(sample_profile, query)
        
        # نمایش توضیحات به صورت زیبا
        if "explanation" in result:
            print("\n" + "="*60)
            print("📄 IMMIGRATION RECOMMENDATION")
            print("="*60 + "\n")
            print(result["explanation"])
        
        # نمایش جزئیات تکنیکی
        print("\n" + "="*60)
        print("📊 TECHNICAL DETAILS")
        print("="*60)
        result_copy = result.copy()
        result_copy.pop("explanation", None)
        print(json.dumps(result_copy, indent=2, ensure_ascii=False))
        print("="*60 + "\n")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error in demo: {str(e)}")


def test_agents():
    """Test individual agents"""
    print_banner()
    print("\n=== TESTING AGENTS ===\n")
    
    try:
        # Test imports
        print("✓ Testing imports...")
        from agents.profile_agent import ProfileAgent
        from agents.country_finder_agent import CountryFinderAgent
        from agents.match_agent import MatchAgent
        from agents.explain_agent import ExplainAgent
        from memory.session_service import SessionService
        from agents.orchestrator import Orchestrator
        
        print("✓ All agents imported successfully!")
        
        # Test session service
        print("✓ Testing session service...")
        session_service = SessionService()
        print("✓ Session service initialized!")
        
        # Test orchestrator
        print("✓ Testing orchestrator...")
        orchestrator = Orchestrator(session_service)
        print("✓ Orchestrator initialized!")
        
        print("\n✅ All components are working correctly!\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()



def main():
    """Main application entry point"""
    
    # Show menu if no arguments
    if len(sys.argv) == 1:
        print_banner()
        print_colored("📋 SELECT MODE:", Colors.BOLD + Colors.CYAN)
        print_colored("━" * 60, Colors.CYAN)
        print(f"\n  {Colors.BOLD}1.{Colors.ENDC} Interactive Mode - Answer questions step by step")
        print(f"  {Colors.BOLD}2.{Colors.ENDC} Demo Mode - See a quick example")
        print(f"  {Colors.BOLD}3.{Colors.ENDC} Test Mode - Verify system components")
        print(f"  {Colors.BOLD}4.{Colors.ENDC} Exit")
        print_colored("\n" + "━" * 60, Colors.CYAN)
        
        choice = input(f"\n{Colors.BOLD}Enter your choice (1-4):{Colors.ENDC} ").strip()
        
        if choice == "1":
            interactive_mode()
        elif choice == "2":
            demo_mode()
        elif choice == "3":
            test_agents()
        elif choice == "4":
            print_colored("\n👋 Goodbye!", Colors.GREEN)
            sys.exit(0)
        else:
            print_colored(f"\n❌ Invalid choice: {choice}", Colors.RED)
            print_colored("Please run again and select 1-4\n", Colors.YELLOW)
            sys.exit(1)
    
    # Command line arguments
    else:
        mode = sys.argv[1].lower()
        
        if mode == "demo":
            demo_mode()
        elif mode == "test":
            test_agents()
        elif mode in ["interactive", "i"]:
            interactive_mode()
        else:
            print_colored(f"❌ Unknown mode: {mode}", Colors.RED)
            print("\nUsage:")
            print(f"  {Colors.BOLD}python main.py{Colors.ENDC}              - Show menu")
            print(f"  {Colors.BOLD}python main.py demo{Colors.ENDC}         - Run demo")
            print(f"  {Colors.BOLD}python main.py test{Colors.ENDC}         - Test system")
            print(f"  {Colors.BOLD}python main.py interactive{Colors.ENDC}  - Interactive mode")
            print()
            sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
