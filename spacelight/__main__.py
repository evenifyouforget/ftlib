import argparse
from .__init__ import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Spacelight Tournament")
    parser.add_argument('-a', '--max-mode', action='store_true', help='Enable maximum features (all levels, longer autotune)')
    parser.add_argument('-n', '--max-levels', type=int, default=None, help='Override for number of levels to load')
    parser.add_argument('-t', '--autotune-time', type=float, default=None, help='Override for auto-tuning time budget')
    
    args = parser.parse_args()
    
    main(max_mode=args.max_mode, max_levels=args.max_levels, autotune_time=args.autotune_time)