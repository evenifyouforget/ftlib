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

# Import everything from the new modular structure
from spacelight import *

# Backwards compatibility: expose main function
if __name__ == "__main__":
    main()