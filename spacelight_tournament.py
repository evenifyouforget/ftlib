#!/usr/bin/env python3
"""
Spacelight Tournament: Research framework for goal rectangle checking
Generation 5 TDD checker research
"""

import argparse
import sys
import time
from abc import ABC, abstractmethod
from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional
import math
import pandas as pd
import numpy as np
from scipy import optimize
import warnings
import subprocess
import json

# Add test directory to path for imports
sys.path.append(str(Path(__file__).parent / 'test'))
from get_design import retrieveLevel, retrieveDesign, designDomToStruct, fcsim_piece_types

@dataclass
class EasyLevel:
    """Simplified struct for easy test cases with 9 values total"""
    # Goal area: x, y, w, h
    goal_x: float
    goal_y: float 
    goal_w: float
    goal_h: float
    # Goal rectangle: x, y, w, h, angle
    rect_x: float
    rect_y: float
    rect_w: float
    rect_h: float
    rect_angle: float
    # Metadata
    level_id: Optional[str] = None
    expected_result: Optional[bool] = None

class Contestant(ABC):
    """Base class for goal checking contestants"""
    
    @abstractmethod
    def name(self) -> str:
        """Return the contestant name (typically class name)"""
        return self.__class__.__name__
    
    @abstractmethod 
    def guess_does_solve(self, level: EasyLevel) -> bool:
        """Predict if the goal rectangle is inside the goal area"""
        pass

class ParameterizedContestant(Contestant):
    """Base class for contestants with tunable parameters"""
    
    def __init__(self, params: Dict[str, float]):
        self.params = params.copy()
    
    def name(self) -> str:
        """Include parameters in name without rounding"""
        param_str = "_".join(f"{k}={v}" for k, v in self.params.items())
        return f"{self.__class__.__name__}({param_str})"
    
    @abstractmethod
    def get_param_bounds(self) -> Dict[str, Tuple[float, float]]:
        """Return parameter bounds as {param_name: (min_value, max_value)}"""
        pass
    
    def set_params(self, params: Dict[str, float]):
        """Update parameters"""
        self.params = params.copy()

class SpaceLightTournament:
    """Tournament system to evaluate goal checking contestants"""
    
    def __init__(self, easy_levels: List[EasyLevel]):
        self.easy_levels = easy_levels
        self.contestants: List[Contestant] = []
    
    def add_contestant(self, contestant: Contestant):
        """Add a contestant to the tournament"""
        self.contestants.append(contestant)
    
    def run_tournament(self, timeout_seconds: Optional[float] = None) -> Dict[str, Any]:
        """Run tournament and return results"""
        results = {}
        
        print(f"🚀 Spacelight Tournament: Testing {len(self.contestants)} contestants on {len(self.easy_levels)} easy levels")
        print("=" * 80)
        
        start_time = time.time()
        
        for contestant in self.contestants:
            if timeout_seconds and (time.time() - start_time) > timeout_seconds:
                print(f"⏰ Tournament timeout reached, stopping at {contestant.name()}")
                break
                
            contestant_start = time.time()
            correct_predictions = 0
            total_predictions = 0
            
            for level in self.easy_levels:
                if level.expected_result is not None:
                    prediction = contestant.guess_does_solve(level)
                    if prediction == level.expected_result:
                        correct_predictions += 1
                    total_predictions += 1
            
            pass_rate = correct_predictions / total_predictions if total_predictions > 0 else 0
            contestant_time = time.time() - contestant_start
            
            results[contestant.name()] = {
                'pass_rate': pass_rate,
                'correct': correct_predictions,
                'total': total_predictions,
                'time_seconds': contestant_time
            }
            
            print(f"{contestant.name():<60} | Pass Rate: {pass_rate:.4f} ({correct_predictions}/{total_predictions}) | Time: {contestant_time:.3f}s")
        
        total_time = time.time() - start_time
        print("=" * 80)
        print(f"🏁 Tournament completed in {total_time:.3f}s")
        
        return results

def load_easy_levels_from_tsv(max_levels: int = None) -> List[EasyLevel]:
    """Load and filter levels to easy cases from fc_data.tsv"""
    print("📥 Loading levels from fc_data.tsv...")
    
    tsv_path = Path(__file__).parent / 'test' / 'fc_data.tsv'
    easy_levels = []
    
    # Read the TSV file
    with open(tsv_path, 'r') as f:
        lines = f.readlines()
    
    for line_num, line in enumerate(lines, 1):
        if max_levels and len(easy_levels) >= max_levels:
            print(f"🛑 Reached max_levels limit ({max_levels})")
            break
            
        line = line.strip()
        if not line:
            continue
            
        parts = line.split('\t')
        if len(parts) < 1:
            continue
            
        url = parts[0].strip()
        if not url:
            continue
            
        # Extract level/design ID from URL
        level_id = None
        if 'levelId=' in url:
            level_id = url.split('levelId=')[1].split('&')[0]
            is_design = False
        elif 'designId=' in url:
            level_id = url.split('designId=')[1].split('&')[0] 
            is_design = True
        else:
            continue
            
        # Skip if we can't parse it
        if not level_id:
            continue
            
        print(f"📦 Processing {url}...")
        
        try:
            # Download and parse the level
            dom = retrieveDesign(level_id) if is_design else retrieveLevel(level_id)
            design_struct = designDomToStruct(dom)
            
            # Filter to easy cases: build area + goal area + exactly one goal rectangle
            if (len(design_struct.goal_pieces) == 1 and 
                design_struct.goal_pieces[0].type_id == fcsim_piece_types.FCSIM_GP_RECT.value and
                design_struct.build_area and design_struct.goal_area):
                
                goal_piece = design_struct.goal_pieces[0]
                
                easy_level = EasyLevel(
                    goal_x=design_struct.goal_area.x,
                    goal_y=design_struct.goal_area.y,
                    goal_w=design_struct.goal_area.w,
                    goal_h=design_struct.goal_area.h,
                    rect_x=goal_piece.x,
                    rect_y=goal_piece.y,
                    rect_w=goal_piece.w,
                    rect_h=goal_piece.h,
                    rect_angle=goal_piece.angle,
                    level_id=level_id,
                    expected_result=None  # We'll determine this via ftlib
                )
                
                easy_levels.append(easy_level)
                print(f"✅ Added easy level: {level_id}")
            else:
                print(f"⏭️  Skipped complex level: {level_id}")
                
        except Exception as e:
            print(f"❌ Failed to process {level_id}: {e}")
            continue
    
    print(f"🎯 Found {len(easy_levels)} easy levels")
    return easy_levels

def determine_expected_results_with_ftlib(easy_levels: List[EasyLevel]) -> List[EasyLevel]:
    """Use ftlib to determine expected results for each level"""
    print("🔬 Determining expected results using ftlib...")
    
    cli_adapter = Path(__file__).parent / 'bin' / 'run_single_design'
    if not cli_adapter.exists():
        print("❌ ftlib CLI adapter not found! Run 'scons' first.")
        return easy_levels
    
    for i, level in enumerate(easy_levels):
        if level.level_id:
            try:
                print(f"📊 Checking level {level.level_id} ({i+1}/{len(easy_levels)})")
                
                # Run ftlib to check if design solves
                result = subprocess.run([
                    str(cli_adapter), level.level_id
                ], capture_output=True, text=True, timeout=30)
                
                # Parse output to determine if solved
                solved = 'SOLVED' in result.stdout or result.returncode == 0
                level.expected_result = solved
                
                print(f"  Result: {'✅ SOLVED' if solved else '❌ NOT SOLVED'}")
                
            except Exception as e:
                print(f"  ❌ Error checking {level.level_id}: {e}")
                level.expected_result = None
    
    valid_levels = [l for l in easy_levels if l.expected_result is not None]
    print(f"🎯 Got expected results for {len(valid_levels)}/{len(easy_levels)} levels")
    
    return easy_levels

# ==================== CONTESTANTS ====================

class SaneBasicMathContestant(Contestant):
    """Basic sane math goal rectangle check (reference implementation)"""
    
    def name(self) -> str:
        return "SaneBasicMath"
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        """Check if all 4 corners of rotated rectangle are inside goal area"""
        # Calculate rotated rectangle corners
        angle = level.rect_angle
        hw, hh = level.rect_w / 2, level.rect_h / 2
        
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        
        # Four corners relative to center
        corners = [
            ( hw * cos_a - hh * sin_a,  hw * sin_a + hh * cos_a),
            (-hw * cos_a - hh * sin_a, -hw * sin_a + hh * cos_a),
            (-hw * cos_a + hh * sin_a, -hw * sin_a - hh * cos_a),
            ( hw * cos_a + hh * sin_a,  hw * sin_a - hh * cos_a),
        ]
        
        # Translate to absolute coordinates
        rect_corners = [(level.rect_x + dx, level.rect_y + dy) for dx, dy in corners]
        
        # Check if all corners are inside goal area
        goal_x1, goal_x2 = level.goal_x - level.goal_w/2, level.goal_x + level.goal_w/2
        goal_y1, goal_y2 = level.goal_y - level.goal_h/2, level.goal_y + level.goal_h/2
        
        for x, y in rect_corners:
            if not (goal_x1 <= x <= goal_x2 and goal_y1 <= y <= goal_y2):
                return False
        
        return True

class FCBehaviorBaselineContestant(Contestant):
    """FC behavior baseline: clamp ≥2^15° to -2^15°, truncate to nearest degree"""
    
    def name(self) -> str:
        return "FCBehaviorBaseline"
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        # Apply FC angle processing
        angle_degrees = math.degrees(level.rect_angle)
        
        # Clamp if abs(angle) >= 2^15 degrees (32768)
        if abs(angle_degrees) >= 32768:
            angle_degrees = -32768
        
        # Truncate to nearest degree
        angle_degrees = int(angle_degrees)
        
        # Convert back to radians
        processed_angle = math.radians(angle_degrees)
        
        # Use sane math with processed angle
        hw, hh = level.rect_w / 2, level.rect_h / 2
        cos_a, sin_a = math.cos(processed_angle), math.sin(processed_angle)
        
        corners = [
            ( hw * cos_a - hh * sin_a,  hw * sin_a + hh * cos_a),
            (-hw * cos_a - hh * sin_a, -hw * sin_a + hh * cos_a),
            (-hw * cos_a + hh * sin_a, -hw * sin_a - hh * cos_a),
            ( hw * cos_a + hh * sin_a,  hw * sin_a - hh * cos_a),
        ]
        
        rect_corners = [(level.rect_x + dx, level.rect_y + dy) for dx, dy in corners]
        
        goal_x1, goal_x2 = level.goal_x - level.goal_w/2, level.goal_x + level.goal_w/2
        goal_y1, goal_y2 = level.goal_y - level.goal_h/2, level.goal_y + level.goal_h/2
        
        for x, y in rect_corners:
            if not (goal_x1 <= x <= goal_x2 and goal_y1 <= y <= goal_y2):
                return False
        
        return True

class AlwaysTrueContestant(Contestant):
    """Always predicts true (optimistic)"""
    
    def name(self) -> str:
        return "AlwaysTrue"
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        return True

class AlwaysFalseContestant(Contestant):
    """Always predicts false (pessimistic)"""
    
    def name(self) -> str:
        return "AlwaysFalse"
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        return False

class RandomContestant(Contestant):
    """Random 50/50 predictions"""
    
    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)
    
    def name(self) -> str:
        return f"Random(seed=42)"
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        return self.rng.random() < 0.5

class ParameterizedPaddingContestant(ParameterizedContestant):
    """Parameterized contestant with padding before/after rotation"""
    
    def __init__(self, params: Dict[str, float] = None):
        if params is None:
            params = {'pre_pad': 0.0, 'post_pad': 0.0, 'angle_clamp': 1000.0, 'angle_quantize': 1.0}
        super().__init__(params)
    
    def get_param_bounds(self) -> Dict[str, Tuple[float, float]]:
        return {
            'pre_pad': (-10.0, 10.0),      # Padding before rotation
            'post_pad': (-10.0, 10.0),     # Padding after rotation  
            'angle_clamp': (1.0, 36000.0), # Angle clamping limit (degrees)
            'angle_quantize': (0.1, 10.0)  # Angle quantization step
        }
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        # Apply angle processing
        angle_degrees = math.degrees(level.rect_angle)
        
        # Clamp angle
        clamp_limit = self.params['angle_clamp']
        if abs(angle_degrees) > clamp_limit:
            angle_degrees = -clamp_limit if angle_degrees >= 0 else clamp_limit
        
        # Quantize angle
        quant = self.params['angle_quantize']
        angle_degrees = round(angle_degrees / quant) * quant
        
        processed_angle = math.radians(angle_degrees)
        
        # Apply pre-rotation padding
        pre_pad = self.params['pre_pad']
        rect_w = level.rect_w + 2 * pre_pad
        rect_h = level.rect_h + 2 * pre_pad
        
        # Calculate corners with processed dimensions
        hw, hh = rect_w / 2, rect_h / 2
        cos_a, sin_a = math.cos(processed_angle), math.sin(processed_angle)
        
        corners = [
            ( hw * cos_a - hh * sin_a,  hw * sin_a + hh * cos_a),
            (-hw * cos_a - hh * sin_a, -hw * sin_a + hh * cos_a),
            (-hw * cos_a + hh * sin_a, -hw * sin_a - hh * cos_a),
            ( hw * cos_a + hh * sin_a,  hw * sin_a - hh * cos_a),
        ]
        
        rect_corners = [(level.rect_x + dx, level.rect_y + dy) for dx, dy in corners]
        
        # Apply post-rotation padding to goal area
        post_pad = self.params['post_pad']
        goal_x1 = level.goal_x - level.goal_w/2 - post_pad
        goal_x2 = level.goal_x + level.goal_w/2 + post_pad
        goal_y1 = level.goal_y - level.goal_h/2 - post_pad
        goal_y2 = level.goal_y + level.goal_h/2 + post_pad
        
        for x, y in rect_corners:
            if not (goal_x1 <= x <= goal_x2 and goal_y1 <= y <= goal_y2):
                return False
        
        return True

def autotune_contestant(contestant: ParameterizedContestant, 
                       easy_levels: List[EasyLevel], 
                       max_time_seconds: float = 60) -> ParameterizedContestant:
    """Autotune a parameterized contestant using scipy optimization"""
    print(f"🔧 Auto-tuning {contestant.__class__.__name__} for {max_time_seconds}s...")
    
    bounds = contestant.get_param_bounds()
    param_names = list(bounds.keys())
    param_bounds = [bounds[name] for name in param_names]
    
    def objective_function(param_values):
        """Objective function to minimize (negative pass rate)"""
        params = dict(zip(param_names, param_values))
        contestant.set_params(params)
        
        correct = 0
        total = 0
        for level in easy_levels:
            if level.expected_result is not None:
                prediction = contestant.guess_does_solve(level)
                if prediction == level.expected_result:
                    correct += 1
                total += 1
        
        pass_rate = correct / total if total > 0 else 0
        return -pass_rate  # Minimize negative pass rate = maximize pass rate
    
    # Initial guess (center of bounds)
    initial_guess = [(bounds[name][0] + bounds[name][1]) / 2 for name in param_names]
    
    start_time = time.time()
    
    # Use scipy.optimize with timeout
    def timeout_callback():
        return time.time() - start_time > max_time_seconds
    
    try:
        # Use differential evolution for global optimization
        result = optimize.differential_evolution(
            objective_function, 
            param_bounds,
            maxiter=1000,
            workers=1,
            seed=42
        )
        
        if result.success:
            optimized_params = dict(zip(param_names, result.x))
            contestant.set_params(optimized_params)
            print(f"✅ Optimization succeeded: {optimized_params}")
        else:
            print(f"⚠️  Optimization failed: {result.message}")
            
    except Exception as e:
        print(f"❌ Optimization error: {e}")
    
    elapsed = time.time() - start_time
    print(f"🕐 Tuning completed in {elapsed:.1f}s")
    
    return contestant

def main():
    parser = argparse.ArgumentParser(description='Spacelight Tournament for goal rectangle research')
    parser.add_argument('--timeout', type=float, default=300, 
                       help='Maximum timeout for tournament in seconds (default: 300)')
    parser.add_argument('--skip-ftlib', action='store_true',
                       help='Skip ftlib expected result determination (for testing)')
    parser.add_argument('--autotune-time', type=float, default=60,
                       help='Time to spend auto-tuning parameterized contestants (default: 60)')
    args = parser.parse_args()
    
    print("🌌 Welcome to the Spacelight Tournament!")
    print("🎯 Goal: Research goal rectangle checking algorithms")
    print("🧬 Generation 5 TDD checker research")
    print()
    
    # Load easy test cases
    easy_levels = load_easy_levels_from_tsv(max_levels=10)  # Limit for testing
    
    if not easy_levels:
        print("❌ No easy levels found!")
        return 1
    
    # Determine expected results using ftlib
    if not args.skip_ftlib:
        easy_levels = determine_expected_results_with_ftlib(easy_levels)
        
        # Filter to levels with known results
        valid_levels = [l for l in easy_levels if l.expected_result is not None]
        if len(valid_levels) == 0:
            print("❌ No levels with valid expected results!")
            return 1
        easy_levels = valid_levels
    else:
        print("⚠️  Skipping ftlib expected result determination")
        # Set dummy results for testing
        for level in easy_levels:
            level.expected_result = True  # Dummy value
    
    # Create tournament
    tournament = SpaceLightTournament(easy_levels)
    
    # Add basic contestants
    tournament.add_contestant(SaneBasicMathContestant())
    tournament.add_contestant(FCBehaviorBaselineContestant())
    tournament.add_contestant(AlwaysTrueContestant())
    tournament.add_contestant(AlwaysFalseContestant())
    tournament.add_contestant(RandomContestant(seed=42))
    
    # Add parameterized contestants
    padding_contestant = ParameterizedPaddingContestant()
    tournament.add_contestant(padding_contestant)
    
    # Auto-tune the parameterized contestant
    if args.autotune_time > 0:
        print()
        tuned_contestant = autotune_contestant(
            ParameterizedPaddingContestant(), 
            easy_levels, 
            max_time_seconds=args.autotune_time
        )
        tournament.add_contestant(tuned_contestant)
    
    print()
    # Run tournament
    results = tournament.run_tournament(timeout_seconds=args.timeout)
    
    # Print final summary
    print()
    print("🏆 Final Rankings:")
    sorted_results = sorted(results.items(), key=lambda x: x[1]['pass_rate'], reverse=True)
    for i, (name, result) in enumerate(sorted_results, 1):
        print(f"{i:2d}. {name:<60} | {result['pass_rate']:.4f}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())