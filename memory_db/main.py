# main.py
# Entry point — connects to MongoDB, sets up collections, and runs seed + verify.
# Usage: python main.py [--seed] [--verify] [--all]

import sys
import os

def print_banner():
    print("""
╔══════════════════════════════════════════════════╗
║      Context & Memory Management System          ║
║      Data Layer — Phase 1                        ║
╚══════════════════════════════════════════════════╝
""")

def main():
    print_banner()
    args = sys.argv[1:]

    if not args:
        print("Usage:")
        print("  python main.py --seed      # Setup collections + insert mock data")
        print("  python main.py --verify    # Verify data integrity")
        print("  python main.py --all       # Run both (recommended for first run)")
        sys.exit(0)

    if "--all" in args or "--seed" in args:
        print("── Running Seeder ──────────────────────────────────")
        from data.seed import seed
        seed()

    if "--all" in args or "--verify" in args:
        print("── Running Verifier ────────────────────────────────")
        from data.verify_links import verify
        verify()

if __name__ == "__main__":
    main()
