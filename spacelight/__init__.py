"""Spacelight Tournament - Goal Rectangle Research Framework

A comprehensive framework for testing and optimizing goal rectangle checking algorithms
for Fantastic Contraption level completion prediction.
"""

# Core exports
from .core import EasyLevel, Contestant, ParameterizedContestant, Colors
from .tournament import SpaceLightTournament
from .data_loading import load_easy_levels_from_tsv, determine_expected_results_with_ftlib
from .optimization import autotune_contestant

# Contestant exports
from .contestants import (
    SaneBasicMathContestant,
    FCBehaviorBaselineContestant, 
    AlwaysTrueContestant,
    AlwaysFalseContestant,
    RandomContestant,
    ParameterizedPaddingContestant,
    CenterDistanceContestant,
    BoundingBoxContestant,
    AngleIgnoreContestant,
    ModuloAngleContestant,
    QuantizedAngleContestant,
    ExtremeAngleClampContestant,
    FtlibExactContestant,
    FtlibNoRotationContestant,
    FtlibBoundingBoxContestant,
    FtlibWithClampingContestant
)

# Convenience function for running a complete tournament
def main():
    """Main entry point for running the Spacelight Tournament"""
    levels = load_easy_levels_from_tsv(5)
    levels = determine_expected_results_with_ftlib(levels)
    
    tournament = SpaceLightTournament(levels)
    results = tournament.run_tournament(autotune_time=15)
    
    return results

__all__ = [
    # Core
    'EasyLevel', 'Contestant', 'ParameterizedContestant', 'Colors',
    
    # Main functionality
    'SpaceLightTournament', 'load_easy_levels_from_tsv', 
    'determine_expected_results_with_ftlib', 'autotune_contestant',
    
    # Contestants
    'SaneBasicMathContestant', 'FCBehaviorBaselineContestant',
    'AlwaysTrueContestant', 'AlwaysFalseContestant', 'RandomContestant',
    'ParameterizedPaddingContestant', 'CenterDistanceContestant',
    'BoundingBoxContestant', 'AngleIgnoreContestant', 'ModuloAngleContestant',
    'QuantizedAngleContestant', 'ExtremeAngleClampContestant',
    'FtlibExactContestant', 'FtlibNoRotationContestant',
    'FtlibBoundingBoxContestant', 'FtlibWithClampingContestant',
    
    # Entry point
    'main'
]