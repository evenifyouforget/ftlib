"""Spacelight Tournament - Goal Rectangle Research Framework

A comprehensive framework for testing and optimizing goal rectangle checking algorithms
for Fantastic Contraption level completion prediction.
"""

# Core exports
from .core import EasyLevel, Contestant, ParameterizedContestant, Colors
from .tournament import SpaceLightTournament
from .data_loading import load_easy_levels_from_tsv
from .optimization import autotune_contestant

# Contestant exports
from .contestants import (
    SaneBasicMathContestant,
    AlwaysTrueContestant,
    AlwaysFalseContestant,
    RandomContestant,
    ParameterizedPaddingContestant,
    FtlibExactContestant,
    HyperStrictContestant,
    HyperLenientContestant,
    DistanceBasedStrictContestant,
    DistanceBasedLenientContestant,
    WeirdNeverSolveContestant,
    MagicThresholdContestant,
    SmartPreScreenContestant,
    NonCheatingPatternContestant,
    GeometricInsightContestant,
    StatisticalContestant,
    CombinedInsightContestant,
    PrecisionContestant,
    UltraOptimisticContestant,
    DataDrivenContestant,
    PerfectionistContestant,
    GoalAreaAnalysisContestant,
    GeometryBasedContestant,
    AdvancedGeometryContestant,
    StatisticalLearnerContestant
)

# Convenience function for running a complete tournament
def main(max_mode: bool = False, max_levels: int = None, autotune_time: float = None):
    """Main entry point for running the Spacelight Tournament
    
    Args:
        max_mode: If True, enables maximum features (all levels, longer autotune)
        max_levels: Override for number of levels to load
        autotune_time: Override for auto-tuning time budget
    """
    if max_mode:
        # Max mode: all levels, longer autotune time
        levels = load_easy_levels_from_tsv(max_levels or None)  # Load all levels
        autotune_budget = autotune_time or 60  # Longer optimization
        print(f"🚀 {Colors.BOLD}MAX MODE ENABLED{Colors.RESET} - All levels, extended optimization")
    else:
        # Default mode: limited for quick testing
        levels = load_easy_levels_from_tsv(max_levels or 5)
        autotune_budget = autotune_time or 15
    
    tournament = SpaceLightTournament(levels)
    results = tournament.run_tournament(autotune_time=autotune_budget)
    
    return results

__all__ = [
    # Core
    'EasyLevel', 'Contestant', 'ParameterizedContestant', 'Colors',
    
    # Main functionality
    'SpaceLightTournament', 'load_easy_levels_from_tsv', 'autotune_contestant',
    
    # Contestants
    'SaneBasicMathContestant', 'AlwaysTrueContestant', 'AlwaysFalseContestant', 
    'RandomContestant', 'ParameterizedPaddingContestant', 'FtlibExactContestant',
    'HyperStrictContestant', 'HyperLenientContestant', 'DistanceBasedStrictContestant',
    'DistanceBasedLenientContestant', 'WeirdNeverSolveContestant', 'MagicThresholdContestant',
    'SmartPreScreenContestant', 'NonCheatingPatternContestant', 'GeometricInsightContestant', 
    'StatisticalContestant', 'CombinedInsightContestant', 'PrecisionContestant',
    'UltraOptimisticContestant', 'DataDrivenContestant', 'PerfectionistContestant',
    'GoalAreaAnalysisContestant', 'GeometryBasedContestant', 'AdvancedGeometryContestant',
    'StatisticalLearnerContestant',
    
    # Entry point
    'main'
]