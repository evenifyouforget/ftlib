#!/usr/bin/env python3
"""
🌟 SPACELIGHT TOURNAMENT 🌟

COMPATIBILITY LAYER: This file now imports from the spacelight module.
For new code, import directly from spacelight package.

Example:
    from spacelight import SpaceLightTournament, load_easy_levels_from_tsv
    # or
    import spacelight
    spacelight.main()
"""

import argparse
# Import everything from the new modular structure
from spacelight import *

# CLI interface with backwards compatibility
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spacelight Tournament - Goal Rectangle Research")
    parser.add_argument("-m", "--max-mode", action="store_true", 
                       help="Enable max mode: all levels, extended optimization (60s autotune)")
    parser.add_argument("-l", "--max-levels", type=int, 
                       help="Maximum number of levels to load (default: 5, max-mode: all)")
    parser.add_argument("-t", "--autotune-time", type=float,
                       help="Auto-tuning time budget in seconds (default: 15s, max-mode: 60s)")
    
    args = parser.parse_args()
    
    if args.max_mode:
        print(f"🚀 {Colors.BOLD}MAX MODE ENABLED{Colors.RESET}")
        print("   • Loading all available levels")
        print("   • Extended 60s auto-tuning budget")
        print("   • All contestants enabled")
        print()
    
    main(max_mode=args.max_mode, 
         max_levels=args.max_levels, 
         autotune_time=args.autotune_time)