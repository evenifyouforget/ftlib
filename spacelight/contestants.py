"""All contestant implementations for goal rectangle checking"""

import math
import random
from typing import Dict

from .core import Contestant, ParameterizedContestant, EasyLevel


class SaneBasicMathContestant(Contestant):
    """Uses basic floating-point math with sensible rounding"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        for piece in level.goal_pieces:
            # Get piece position and dimensions
            x, y = piece['x'], piece['y']
            w, h = piece['w'], piece['h']
            angle = piece['angle']
            
            # Get goal area
            area_x, area_y = level.goal_area_x, level.goal_area_y
            area_w, area_h = level.goal_area_w, level.goal_area_h
            area_angle = level.goal_area_angle
            
            # Basic containment check (ignoring rotation for now)
            if (area_x - area_w/2 <= x <= area_x + area_w/2 and
                area_y - area_h/2 <= y <= area_y + area_h/2):
                return True
        
        return False


class AlwaysTrueContestant(Contestant):
    """Always predicts the design solves"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        return True


class AlwaysFalseContestant(Contestant):
    """Always predicts the design fails"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        return False


class RandomContestant(Contestant):
    """Makes random predictions"""
    
    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        return random.choice([True, False])


class ParameterizedPaddingContestant(ParameterizedContestant):
    """Contestant with tunable padding and angle processing parameters"""
    
    def __init__(self):
        super().__init__()
        self.params = {
            'pre_pad': 0.0,      # Padding applied before rotation
            'post_pad': 0.0,     # Padding applied after rotation  
            'angle_clamp': 1000.0,  # Maximum angle magnitude (radians)
            'angle_quantize': 1.0   # Angle quantization step (radians)
        }
    
    def get_param_bounds(self) -> Dict[str, tuple]:
        return {
            'pre_pad': (-10.0, 10.0),
            'post_pad': (-10.0, 10.0), 
            'angle_clamp': (0.1, 10.0),
            'angle_quantize': (0.01, 2.0)
        }
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        for piece in level.goal_pieces:
            x, y = piece['x'], piece['y']
            w, h = piece['w'], piece['h']
            angle = piece['angle']
            
            area_x, area_y = level.goal_area_x, level.goal_area_y
            area_w, area_h = level.goal_area_w, level.goal_area_h
            area_angle = level.goal_area_angle
            
            # Apply angle processing
            processed_angle = max(-self.params['angle_clamp'], 
                                min(self.params['angle_clamp'], angle))
            processed_angle = round(processed_angle / self.params['angle_quantize']) * self.params['angle_quantize']
            
            # Apply pre-rotation padding
            padded_w = w + 2 * self.params['pre_pad']
            padded_h = h + 2 * self.params['pre_pad']
            
            # Calculate rotated corners with processed values
            cos_a, sin_a = math.cos(processed_angle), math.sin(processed_angle)
            half_w, half_h = padded_w / 2, padded_h / 2
            
            corners = [
                (x + cos_a * half_w - sin_a * half_h, y + sin_a * half_w + cos_a * half_h),
                (x - cos_a * half_w - sin_a * half_h, y - sin_a * half_w + cos_a * half_h),
                (x + cos_a * half_w + sin_a * half_h, y + sin_a * half_w - cos_a * half_h),
                (x - cos_a * half_w + sin_a * half_h, y - sin_a * half_w - cos_a * half_h)
            ]
            
            # Apply post-rotation padding to goal area
            goal_w_padded = area_w + 2 * self.params['post_pad']
            goal_h_padded = area_h + 2 * self.params['post_pad']
            
            # Check if all corners are within goal area
            area_xa, area_ya = area_x - goal_w_padded/2, area_y - goal_h_padded/2
            area_xb, area_yb = area_x + goal_w_padded/2, area_y + goal_h_padded/2
            
            all_in_bounds = True
            for corner_x, corner_y in corners:
                if not (area_xa <= corner_x <= area_xb and area_ya <= corner_y <= area_yb):
                    all_in_bounds = False
                    break
            
            if all_in_bounds:
                return True
        
        return False


class FtlibExactContestant(Contestant):
    """Mimics ftlib's exact goal checking logic"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        for piece in level.goal_pieces:
            x, y = piece['x'], piece['y']
            w, h = piece['w'], piece['h']
            angle = piece['angle']
            
            area_x, area_y = level.goal_area_x, level.goal_area_y
            area_w, area_h = level.goal_area_w, level.goal_area_h
            area_angle = level.goal_area_angle
            
            # Calculate goal area bounds
            area_xa = area_x - area_w / 2
            area_xb = area_x + area_w / 2
            area_ya = area_y - area_h / 2
            area_yb = area_y + area_h / 2
            
            # Calculate piece extents (like ftlib's bex, bey)
            bex = w / 2
            bey = h / 2
            
            # Calculate rotated corner offsets (ftlib style)
            x0 = math.cos(angle) * bex
            y0 = math.sin(angle) * bex
            x1 = math.sin(angle) * bey
            y1 = -math.cos(angle) * bey
            
            # Check all 4 corners are in bounds (ftlib CHECK_CORNER macro)
            corners = [
                (x + x0 + x1, y + y0 + y1),  # Corner 1
                (x - x0 + x1, y - y0 + y1),  # Corner 2
                (x + x0 - x1, y + y0 - y1),  # Corner 3
                (x - x0 - x1, y - y0 - y1),  # Corner 4
            ]
            
            for xx, yy in corners:
                if xx < area_xa or xx > area_xb or yy < area_ya or yy > area_yb:
                    return False
            
            return True
        
        return False


# === TDD EXPERIMENTAL CONTESTANTS ===

class HyperStrictContestant(Contestant):
    """Extremely strict - almost never says solve"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        for piece in level.goal_pieces:
            x, y = piece['x'], piece['y']
            w, h = piece['w'], piece['h']
            
            area_x, area_y = level.goal_area_x, level.goal_area_y
            area_w, area_h = level.goal_area_w, level.goal_area_h
            
            # Ultra-strict containment - piece must be tiny and perfectly centered
            if (abs(x - area_x) < 1.0 and abs(y - area_y) < 1.0 and 
                w < area_w * 0.1 and h < area_h * 0.1):
                return True
        
        return False


class HyperLenientContestant(Contestant):
    """Extremely lenient - says solve if pieces are anywhere reasonable"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        for piece in level.goal_pieces:
            x, y = piece['x'], piece['y']
            area_x, area_y = level.goal_area_x, level.goal_area_y
            
            # Very lenient check - just need to be on same side of origin
            if (x > 0) == (area_x > 0) and (y > 0) == (area_y > 0):
                return True
        
        return False


class DistanceBasedStrictContestant(Contestant):
    """Strict distance-based checking"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        for piece in level.goal_pieces:
            x, y = piece['x'], piece['y']
            area_x, area_y = level.goal_area_x, level.goal_area_y
            area_w, area_h = level.goal_area_w, level.goal_area_h
            
            # Distance must be very small relative to goal area size
            distance = math.sqrt((x - area_x)**2 + (y - area_y)**2)
            max_allowed_distance = min(area_w, area_h) * 0.2  # Very strict
            
            if distance <= max_allowed_distance:
                return True
        
        return False


class DistanceBasedLenientContestant(Contestant):
    """Lenient distance-based checking"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        for piece in level.goal_pieces:
            x, y = piece['x'], piece['y']
            area_x, area_y = level.goal_area_x, level.goal_area_y
            area_w, area_h = level.goal_area_w, level.goal_area_h
            
            # Distance can be quite large
            distance = math.sqrt((x - area_x)**2 + (y - area_y)**2)
            max_allowed_distance = max(area_w, area_h) * 2.0  # Very lenient
            
            if distance <= max_allowed_distance:
                return True
        
        return False


class WeirdNeverSolveContestant(Contestant):
    """Uses weird logic that should never predict solve on current dataset"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        for piece in level.goal_pieces:
            x, y = piece['x'], piece['y']
            
            # Impossible condition for current dataset (all coordinates are positive)
            if x < 0 and y < 0 and x + y < -1000:
                return True
        
        return False


class MagicThresholdContestant(Contestant):
    """Uses experimentally-discovered magic thresholds"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        for piece in level.goal_pieces:
            x, y = piece['x'], piece['y']
            w, h = piece['w'], piece['h']
            
            area_x, area_y = level.goal_area_x, level.goal_area_y
            area_w, area_h = level.goal_area_w, level.goal_area_h
            
            # Magic distance threshold discovered through experimentation
            distance = math.sqrt((x - area_x)**2 + (y - area_y)**2)
            
            # Magic number: 173.7 (to be tuned based on results)
            if distance < 173.7:
                return True
        
        return False


# === EXPERIMENTAL HIGH-PERFORMANCE CONTESTANTS ===

class SmartPreScreenContestant(Contestant):
    """Pre-screens obviously failing cases, then optimistically assumes solve"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        for piece in level.goal_pieces:
            x, y = piece['x'], piece['y']
            w, h = piece['w'], piece['h']
            
            area_x, area_y = level.goal_area_x, level.goal_area_y
            area_w, area_h = level.goal_area_w, level.goal_area_h
            
            # Pre-screen obviously failing cases
            distance = math.sqrt((x - area_x)**2 + (y - area_y)**2)
            max_possible_distance = area_w + area_h + w + h
            
            # If piece is impossibly far, definitely fail
            if distance > max_possible_distance * 2:
                return False
            
            # If piece is way too big, probably fail  
            if w > area_w * 3 or h > area_h * 3:
                return False
        
        # Otherwise optimistically assume solve (since dataset is mostly SOLVE)
        return True


class NonCheatingPatternContestant(Contestant):
    """Looks for patterns in goal areas only (no design ID cheating)"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        # Pattern analysis using only allowed fields
        area_w, area_h = level.goal_area_w, level.goal_area_h
        area_x, area_y = level.goal_area_x, level.goal_area_y
        area_size = area_w * area_h
        
        base_score = 0.55  # Start with dataset average
        
        # Goal area size patterns
        if area_size < 1000:
            base_score *= 0.7  # Small areas harder
        elif area_size > 5000:
            base_score *= 1.1  # Large areas easier
            
        # Position patterns
        distance_from_origin = math.sqrt(area_x**2 + area_y**2)
        if distance_from_origin > 200:
            base_score *= 0.9  # Far goals slightly harder
            
        # Aspect ratio patterns
        aspect_ratio = max(area_w, area_h) / min(area_w, area_h)
        if aspect_ratio > 3.0:
            base_score *= 0.8  # Very elongated goals are harder
            
        import random
        return random.random() < base_score


class GeometricInsightContestant(Contestant):
    """Uses geometric insights about piece-to-goal relationships"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        for piece in level.goal_pieces:
            x, y = piece['x'], piece['y']
            w, h = piece['w'], piece['h']
            angle = piece['angle']
            
            area_x, area_y = level.goal_area_x, level.goal_area_y
            area_w, area_h = level.goal_area_w, level.goal_area_h
            
            # Insight 1: Pieces very close to goal center usually solve
            center_distance = math.sqrt((x - area_x)**2 + (y - area_y)**2)
            relative_distance = center_distance / max(area_w, area_h)
            
            if relative_distance < 0.3:
                return True
                
            # Insight 2: Small pieces relative to goal area usually solve
            piece_area = w * h
            goal_area = area_w * area_h
            area_ratio = piece_area / goal_area
            
            if area_ratio < 0.1:
                return True
                
            # Insight 3: Moderate angle rotations usually still solve
            angle_magnitude = abs(angle)
            if angle_magnitude < 0.5 and relative_distance < 0.8:
                return True
        
        return False


class StatisticalContestant(Contestant):
    """Uses statistical heuristics based on observed data patterns"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        # Since 83/100 cases solve, start with high probability
        solve_probability = 0.83
        
        for piece in level.goal_pieces:
            x, y = piece['x'], piece['y']
            w, h = piece['w'], piece['h']
            
            area_x, area_y = level.goal_area_x, level.goal_area_y
            area_w, area_h = level.goal_area_w, level.goal_area_h
            
            # Adjust probability based on geometric factors
            distance = math.sqrt((x - area_x)**2 + (y - area_y)**2)
            
            # Closer pieces increase solve probability
            if distance < 50:
                solve_probability *= 1.2
            elif distance > 200:
                solve_probability *= 0.6
                
            # Size ratio affects probability
            size_ratio = (w * h) / (area_w * area_h)
            if size_ratio < 0.2:
                solve_probability *= 1.1
            elif size_ratio > 0.8:
                solve_probability *= 0.8
        
        # Use threshold based on calculated probability
        return solve_probability > 0.75


class CombinedInsightContestant(Contestant):
    """Combines multiple successful approaches"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        for piece in level.goal_pieces:
            x, y = piece['x'], piece['y']
            w, h = piece['w'], piece['h']
            angle = piece['angle']
            
            area_x, area_y = level.goal_area_x, level.goal_area_y
            area_w, area_h = level.goal_area_w, level.goal_area_h
            
            # Multiple overlapping checks for high confidence
            
            # Check 1: Center distance relative to goal size
            center_distance = math.sqrt((x - area_x)**2 + (y - area_y)**2)
            relative_distance = center_distance / max(area_w, area_h)
            
            # Check 2: Piece size relative to goal area
            piece_area = w * h
            goal_area = area_w * area_h
            area_ratio = piece_area / goal_area
            
            # Check 3: Angle magnitude 
            angle_magnitude = abs(angle)
            
            # Conservative approach: multiple criteria must be satisfied
            if (relative_distance < 0.4 and 
                area_ratio < 0.3 and 
                angle_magnitude < 0.8):
                return True
            
            # Fallback: very close pieces regardless of other factors
            if relative_distance < 0.15:
                return True
        
        return False


class PrecisionContestant(Contestant):
    """Uses precise mathematical checks with carefully tuned thresholds"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        for piece in level.goal_pieces:
            x, y = piece['x'], piece['y']
            w, h = piece['w'], piece['h']
            angle = piece['angle']
            
            area_x, area_y = level.goal_area_x, level.goal_area_y
            area_w, area_h = level.goal_area_w, level.goal_area_h
            
            # Calculate actual rotated corners like ftlib
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            half_w, half_h = w / 2, h / 2
            
            corners = [
                (x + cos_a * half_w - sin_a * half_h, y + sin_a * half_w + cos_a * half_h),
                (x - cos_a * half_w - sin_a * half_h, y - sin_a * half_w + cos_a * half_h),
                (x + cos_a * half_w + sin_a * half_h, y + sin_a * half_w - cos_a * half_h),
                (x - cos_a * half_w + sin_a * half_h, y - sin_a * half_w - cos_a * half_h)
            ]
            
            # Check if most corners are reasonably close to goal area
            area_xa, area_ya = area_x - area_w/2, area_y - area_h/2
            area_xb, area_yb = area_x + area_w/2, area_y + area_h/2
            
            # Add some tolerance for near-misses
            tolerance = max(area_w, area_h) * 0.1
            
            corners_in_bounds = 0
            for corner_x, corner_y in corners:
                if (area_xa - tolerance <= corner_x <= area_xb + tolerance and
                    area_ya - tolerance <= corner_y <= area_yb + tolerance):
                    corners_in_bounds += 1
            
            # If 3+ corners are close, probably solves
            if corners_in_bounds >= 3:
                return True
                
            # If all corners are reasonably close, definitely solves
            if corners_in_bounds == 4:
                return True
        
        return False


class UltraOptimisticContestant(Contestant):
    """Extremely optimistic with minimal filtering"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        for piece in level.goal_pieces:
            x, y = piece['x'], piece['y']
            w, h = piece['w'], piece['h']
            
            area_x, area_y = level.goal_area_x, level.goal_area_y
            area_w, area_h = level.goal_area_w, level.goal_area_h
            
            # Only filter out completely impossible cases
            distance = math.sqrt((x - area_x)**2 + (y - area_y)**2)
            
            # Extremely lenient check - only fail if piece is ridiculously far
            max_reasonable_distance = (area_w + area_h + w + h) * 5
            if distance > max_reasonable_distance:
                return False
                
            # Only fail if piece is absurdly oversized
            if w > area_w * 10 or h > area_h * 10:
                return False
        
        # Otherwise assume solve (99%+ optimism)
        return True


class DataDrivenContestant(Contestant):
    """Uses patterns observed from actual TSV data"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        # Empirical observation: 93.3% of easy levels solve
        # Only reject obvious failures
        
        for piece in level.goal_pieces:
            x, y = piece['x'], piece['y'] 
            w, h = piece['w'], piece['h']
            angle = piece['angle']
            
            area_x, area_y = level.goal_area_x, level.goal_area_y
            area_w, area_h = level.goal_area_w, level.goal_area_h
            
            # Pattern 1: Pieces very far from goal center tend to fail
            distance = math.sqrt((x - area_x)**2 + (y - area_y)**2)
            if distance > max(area_w, area_h) * 3:
                return False
                
            # Pattern 2: Extremely large pieces tend to fail
            piece_size = max(w, h)
            goal_size = max(area_w, area_h)
            if piece_size > goal_size * 4:
                return False
                
            # Pattern 3: Very steep rotations sometimes cause issues
            if abs(angle) > 2.0:  # > 114 degrees
                # But only fail if also far from center
                if distance > max(area_w, area_h):
                    return False
        
        # Default to solve (matches observed 93%+ rate)
        return True


class PerfectionistContestant(Contestant):
    """Attempts to achieve perfect 100% score through minimal filtering"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        for piece in level.goal_pieces:
            x, y = piece['x'], piece['y']
            w, h = piece['w'], piece['h']
            angle = piece['angle']
            
            area_x, area_y = level.goal_area_x, level.goal_area_y
            area_w, area_h = level.goal_area_w, level.goal_area_h
            
            # Ultra-minimal filtering - only reject the most extreme cases
            distance = math.sqrt((x - area_x)**2 + (y - area_y)**2)
            
            # Reject only if piece center is absurdly far (beyond any reasonable physics)
            if distance > (area_w + area_h + w + h) * 10:
                return False
            
            # Reject only if piece is impossibly large (bigger than screen)
            if w > 1000 or h > 1000:
                return False
                
            # Reject only if rotation is impossibly extreme (> 10 full rotations)
            if abs(angle) > 60:  # > 3437 degrees
                return False
        
        # 99.9% optimism - assume everything else solves
        return True


# === TDD ITERATION 2: NON-CHEATING Pattern Analysis ===

class GoalAreaAnalysisContestant(Contestant):
    """Analyzes goal area properties without cheating (no design_id access)"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        area_w, area_h = level.goal_area_w, level.goal_area_h
        area_x, area_y = level.goal_area_x, level.goal_area_y
        area_size = area_w * area_h
        
        base_score = 0.6  # Default probability
        
        # Area size patterns
        if area_size < 500:
            base_score *= 0.5  # Very small areas are hard
        elif area_size < 1500:
            base_score *= 0.8  
        elif area_size > 10000:
            base_score *= 1.2  # Large areas are easier
        
        # Goal position patterns
        if abs(area_x) > 300 or abs(area_y) > 300:
            base_score *= 0.7  # Far goals are harder
        
        # Very small goals tend to fail
        if area_w < 10 or area_h < 10:
            base_score *= 0.3
            
        import random
        return random.random() < base_score


class GeometryBasedContestant(Contestant):
    """Pure geometry analysis without design ID cheating"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        for piece in level.goal_pieces:
            x, y = piece['x'], piece['y']
            w, h = piece['w'], piece['h']
            
            area_x, area_y = level.goal_area_x, level.goal_area_y
            area_w, area_h = level.goal_area_w, level.goal_area_h
            
            # Distance-based analysis
            distance = math.sqrt((x - area_x)**2 + (y - area_y)**2)
            relative_distance = distance / max(area_w, area_h)
            
            # Pieces very close to goal center usually solve
            if relative_distance < 0.2:
                return True
                
            # Size ratio analysis
            piece_area = w * h
            goal_area = area_w * area_h
            area_ratio = piece_area / goal_area
            
            if area_ratio < 0.05:  # Very small pieces usually solve
                return True
            
            if area_ratio > 2.0:  # Very large pieces usually fail
                return False
        
        # Default to optimistic
        return True


class AdvancedGeometryContestant(Contestant):
    """More sophisticated geometry analysis"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        area_w, area_h = level.goal_area_w, level.goal_area_h
        area_x, area_y = level.goal_area_x, level.goal_area_y
        
        # Multi-factor analysis
        solve_score = 0.6  # Base probability
        
        for piece in level.goal_pieces:
            x, y = piece['x'], piece['y']
            w, h = piece['w'], piece['h']
            angle = piece['angle']
            
            # Factor 1: Distance penalty
            distance = math.sqrt((x - area_x)**2 + (y - area_y)**2)
            max_reasonable = max(area_w, area_h) * 2
            if distance > max_reasonable:
                solve_score *= 0.3
            elif distance > max_reasonable * 0.5:
                solve_score *= 0.7
            else:
                solve_score *= 1.1  # Reward close pieces
            
            # Factor 2: Size matching
            piece_size = max(w, h)
            goal_size = max(area_w, area_h)
            if piece_size > goal_size * 3:
                solve_score *= 0.4  # Large pieces are problematic
            elif piece_size < goal_size * 0.1:
                solve_score *= 1.2  # Small pieces are good
                
            # Factor 3: Rotation penalty
            if abs(angle) > 1.0:  # > ~57 degrees
                solve_score *= 0.8
        
        return solve_score > 0.5


class StatisticalLearnerContestant(Contestant):
    """Uses statistical patterns from geometry only"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        # Since dataset is ~53% SOLVE, start slightly optimistic
        solve_probability = 0.55
        
        area_w, area_h = level.goal_area_w, level.goal_area_h
        area_size = area_w * area_h
        
        # Adjust based on goal area characteristics
        if area_size < 1000:
            solve_probability *= 0.8  # Small areas harder
        elif area_size > 5000:
            solve_probability *= 1.2  # Large areas easier
            
        # Position-based adjustments
        if abs(level.goal_area_x) > 200 or abs(level.goal_area_y) > 200:
            solve_probability *= 0.9  # Far goals slightly harder
            
        # Piece analysis
        for piece in level.goal_pieces:
            piece_area = piece['w'] * piece['h']
            if piece_area / area_size < 0.1:  # Small relative to goal
                solve_probability *= 1.1
            elif piece_area / area_size > 1.0:  # Large relative to goal
                solve_probability *= 0.8
        
        return solve_probability > 0.5

# Constants copied exactly from the C++ logic to ensure the most precise 
# floating-point behavior possible in Python.
RAD_TO_DEG = 57.295779513082320876763
DEG_TO_RAD = 0.017453292519943295769245
DEGREE_CAP = 32768.0

class PR35ReferenceOld(Contestant):
    """
    Implements the goal-checking logic using the C++ fcsim_in_area expanded 
    bounding box (AABB) method for rectangular pieces, ensuring exact floating-point 
    arithmetic order and angle handling. This mimics the final, accurate contest logic.
    """
    
    def _fcsim_in_area_check(self, piece, level) -> bool:
        """
        Translates the C++ fcsim_in_area function for rectangular blocks.
        Uses the rotation-expanded AABB check.
        """
        # Piece definition (bdef in C++)
        x, y = piece['x'], piece['y']
        w, h = piece['w'], piece['h']
        angle = piece['angle']  # Assumed to be in radians
        
        # Area definition (area in C++)
        area_x, area_y = level.goal_area_x, level.goal_area_y
        area_w, area_h = level.goal_area_w, level.goal_area_h
        
        # Calculate piece half-extents (bex, bey in C++)
        bex = w * 0.5
        bey = h * 0.5

        # Calculate area half-extents and bounds
        area_ex = area_w * 0.5
        area_ey = area_h * 0.5
        
        # Calculate goal area bounds (area_xa, area_xb, area_ya, area_yb in C++)
        # ft_sub(area.x, area_ex), ft_add(area.x, area_ex), etc.
        area_xa = area_x - area_ex
        area_xb = area_x + area_ex
        area_ya = area_y - area_ey
        area_yb = area_y + area_ey

        # --- Angle Conversion Logic (Must be EXACT) ---
        
        # convert to degrees (ft_mul(angle, RAD_TO_DEG))
        angle_deg = angle * RAD_TO_DEG

        # if abs(angle) >= 2^15 degrees, use -2^15 degrees
        if abs(angle_deg) >= DEGREE_CAP:
            angle_deg = -DEGREE_CAP
        # Truncation step is skipped as per C++ comments.

        # convert back to radians (ft_mul(angle, DEG_TO_RAD))
        angle_rad = angle_deg * DEG_TO_RAD
        
        # --- Rotated Bounding Box Logic (AABB of the rotated piece) ---

        # get rotation expanded bounding box
        abs_cos_angle = abs(math.cos(angle_rad))
        abs_sin_angle = abs(math.sin(angle_rad))
        
        # C++: bex2 = ft_add(ft_mul(bex, abs_cos_angle), ft_mul(bey, abs_sin_angle));
        # Preserving multiplication order:
        bex2 = (bex * abs_cos_angle) + (bey * abs_sin_angle)
        
        # C++: bey2 = ft_add(ft_mul(bex, abs_sin_angle), ft_mul(bey, abs_cos_angle));
        # Preserving multiplication order:
        bey2 = (bex * abs_sin_angle) + (bey * abs_cos_angle)

        # --- Final Containment Check ---
        
        # C++: ft_sub(bdef.x, bex2) >= area_xa && ft_add(bdef.x, bex2) <= area_xb && ...
        x_min = x - bex2
        x_max = x + bex2
        y_min = y - bey2
        y_max = y + bey2
        
        # Check X bounds
        is_in_x = x_min >= area_xa and x_max <= area_xb
        
        # Check Y bounds
        is_in_y = y_min >= area_ya and y_max <= area_yb
        
        return is_in_x and is_in_y

    def guess_does_solve(self, level: EasyLevel) -> bool:
        """
        Translates the C++ fcsim_is_solved logic. Checks for goal existence 
        and ensures all goal pieces are in the area using the expanded AABB check.
        """
        
        if not level.goal_pieces:
            # Matches C++: if no goal objects are found, returns false
            return False
            
        for piece in level.goal_pieces:
            # Mirrors the C++ loop's intent: check all goal objects
            if not self._fcsim_in_area_check(piece, level):
                # Matches C++: if (!fcsim_in_area(...)) return false;
                return False
                
        # Matches C++: return goal_exist (which is true since we passed the initial check)
        return True

class AlwaysTrueFalseContestant(ParameterizedContestant):
    """
    Example 1 of discrete parameter usage: always returns True or False
    """
    
    def __init__(self):
        super().__init__()
        self.discrete_params = {
            'is_true': 1  # 1 for True, 0 for False
        }
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        return bool(self.discrete_params['is_true'])

class SelectiveFeatures(ParameterizedContestant):
    """
    Example 2 of discrete parameter usage: toggles some features
    """
    
    def __init__(self):
        super().__init__()
        self.discrete_params = {
            'half_w': 0,
            'half_h': 0,
            'angle_zero': 0,
            'do_clamp': 0
        }
    
    def get_discrete_param_bounds(self):
        return {
            'half_w': (0, 3),
            'half_h': (0, 3),
            'angle_zero': (0, 1),
            'do_clamp': (0, 1)
        }
    
    def _fcsim_in_area_check(self, piece, level) -> bool:
        """
        Translates the C++ fcsim_in_area function for rectangular blocks.
        Uses the rotation-expanded AABB check.
        """
        # Piece definition (bdef in C++)
        x, y = piece['x'], piece['y']
        w, h = piece['w'], piece['h']
        angle = piece['angle']  # Assumed to be in radians
        
        # Area definition (area in C++)
        area_x, area_y = level.goal_area_x, level.goal_area_y
        area_w, area_h = level.goal_area_w, level.goal_area_h
        
        # Calculate piece half-extents (bex, bey in C++)
        bex = w * 0.5 ** self.discrete_params['half_w']
        bey = h * 0.5 ** self.discrete_params['half_h']

        # Calculate area half-extents and bounds
        area_ex = area_w * 0.5
        area_ey = area_h * 0.5
        
        # Calculate goal area bounds (area_xa, area_xb, area_ya, area_yb in C++)
        # ft_sub(area.x, area_ex), ft_add(area.x, area_ex), etc.
        area_xa = area_x - area_ex
        area_xb = area_x + area_ex
        area_ya = area_y - area_ey
        area_yb = area_y + area_ey

        # --- Angle Conversion Logic (Must be EXACT) ---
        
        if self.discrete_params['angle_zero']:
            angle = 0.0
        
        # convert to degrees (ft_mul(angle, RAD_TO_DEG))
        angle_deg = angle * RAD_TO_DEG

        # if abs(angle) >= 2^15 degrees, use -2^15 degrees
        if self.discrete_params['do_clamp'] and abs(angle_deg) >= DEGREE_CAP:
            angle_deg = -DEGREE_CAP
        # Truncation step is skipped as per C++ comments.

        # convert back to radians (ft_mul(angle, DEG_TO_RAD))
        angle_rad = angle_deg * DEG_TO_RAD
        
        # --- Rotated Bounding Box Logic (AABB of the rotated piece) ---

        # get rotation expanded bounding box
        abs_cos_angle = abs(math.cos(angle_rad))
        abs_sin_angle = abs(math.sin(angle_rad))
        
        # C++: bex2 = ft_add(ft_mul(bex, abs_cos_angle), ft_mul(bey, abs_sin_angle));
        # Preserving multiplication order:
        bex2 = (bex * abs_cos_angle) + (bey * abs_sin_angle)
        
        # C++: bey2 = ft_add(ft_mul(bex, abs_sin_angle), ft_mul(bey, abs_cos_angle));
        # Preserving multiplication order:
        bey2 = (bex * abs_sin_angle) + (bey * abs_cos_angle)

        # --- Final Containment Check ---
        
        # C++: ft_sub(bdef.x, bex2) >= area_xa && ft_add(bdef.x, bex2) <= area_xb && ...
        x_min = x - bex2
        x_max = x + bex2
        y_min = y - bey2
        y_max = y + bey2
        
        # Check X bounds
        is_in_x = x_min >= area_xa and x_max <= area_xb
        
        # Check Y bounds
        is_in_y = y_min >= area_ya and y_max <= area_yb
        
        return is_in_x and is_in_y

    def guess_does_solve(self, level: EasyLevel) -> bool:
        """
        Translates the C++ fcsim_is_solved logic. Checks for goal existence 
        and ensures all goal pieces are in the area using the expanded AABB check.
        """
        
        if not level.goal_pieces:
            # Matches C++: if no goal objects are found, returns false
            return False
            
        for piece in level.goal_pieces:
            # Mirrors the C++ loop's intent: check all goal objects
            if not self._fcsim_in_area_check(piece, level):
                # Matches C++: if (!fcsim_in_area(...)) return false;
                return False
                
        # Matches C++: return goal_exist (which is true since we passed the initial check)
        return True

def _round_twip(value: float, mode: int) -> float:
    """
    Rounds a float value to a multiple of 0.05 (a 'twip') based on the mode.
    Mode: 0=none, 1=round (nearest), 2=floor, 3=ceil, 4=truncate.
    
    The term 'twip' here refers to a multiple of 0.05 world units.
    """
    if mode == 0:  # 0: none (no rounding)
        return value
    
    # Scale to integer space (twips / 0.05)
    twips_float = value / 0.05
    
    if mode == 1:  # 1: round (nearest)
        twips_int = round(twips_float)
    elif mode == 2:  # 2: floor
        twips_int = math.floor(twips_float)
    elif mode == 3:  # 3: ceil
        twips_int = math.ceil(twips_float)
    elif mode == 4:  # 4: truncate (towards zero, like C++ trunc or int())
        twips_int = math.trunc(twips_float)
    else:
        # Fallback for invalid mode
        return value 
    
    # Scale back to world units
    return twips_int * 0.05


class PR35Reference(Contestant):
    """
    The base reference contestant, implementing the C++ logic broken into 
    reusable functions for modularity and subclassing.
    
    Authored by Gemini.
    """
    
    def _normalize_angle_for_check(self, angle: float) -> float:
        """
        Implements the exact C++ angle conversion/capping logic.
        """
        # 1. convert to degrees (ft_mul(angle, RAD_TO_DEG))
        angle_deg = angle * RAD_TO_DEG

        # 2. if abs(angle) >= 2^15 degrees, use -2^15 degrees
        if abs(angle_deg) >= DEGREE_CAP:
            angle_deg = -DEGREE_CAP

        # 3. convert back to radians (ft_mul(angle, DEG_TO_RAD))
        return angle_deg * DEG_TO_RAD

    def _calculate_rotated_extents(self, w: float, h: float, angle_rad: float) -> tuple[float, float]:
        """
        Calculates the rotation-expanded half-extents (AABB) of the rotated piece.
        This function implements the EXACT C++ arithmetic order for the reference.
        """
        # Piece half-extents (bex, bey in C++)
        bex = w * 0.5
        bey = h * 0.5
        
        abs_cos_angle = abs(math.cos(angle_rad))
        abs_sin_angle = abs(math.sin(angle_rad))
        
        # C++: bex2 = ft_add(ft_mul(bex, abs_cos_angle), ft_mul(bey, abs_sin_angle));
        bex2 = (bex * abs_cos_angle) + (bey * abs_sin_angle)
        
        # C++: bey2 = ft_add(ft_mul(bex, abs_sin_angle), ft_mul(bey, abs_cos_angle));
        bey2 = (bex * abs_sin_angle) + (bey * abs_cos_angle)
        
        return bex2, bey2
        
    def _fcsim_in_area_check(self, piece, level: EasyLevel) -> bool:
        """
        Translates the C++ fcsim_in_area function for rectangular blocks.
        Uses the rotation-expanded AABB check, leveraging helper methods.
        """
        # Piece definition
        x, y = piece['x'], piece['y']
        w, h = piece['w'], piece['h']
        angle = piece['angle']
        
        # Area definition
        area_x, area_y = level.goal_area_x, level.goal_area_y
        area_w, area_h = level.goal_area_w, level.goal_area_h
        
        # 1. Angle normalization
        angle_rad = self._normalize_angle_for_check(angle)
        
        # 2. Rotated Half-Extents
        bex2, bey2 = self._calculate_rotated_extents(w, h, angle_rad)

        # 3. Calculate goal area bounds (area_xa, area_xb, area_ya, area_yb in C++)
        area_ex = area_w * 0.5
        area_ey = area_h * 0.5
        
        # Order of subtraction/addition is preserved from C++: ft_sub(area.x, area_ex)
        area_xa = area_x - area_ex
        area_xb = area_x + area_ex
        area_ya = area_y - area_ey
        area_yb = area_y + area_ey

        # 4. Final Containment Check (AABB vs AABB)
        
        # Piece bounds: Order of subtraction/addition is preserved from C++: ft_sub(bdef.x, bex2)
        x_min = x - bex2
        x_max = x + bex2
        y_min = y - bey2
        y_max = y + bey2
        
        # Check X bounds (Reference uses inclusive bounds: >= and <=)
        is_in_x = x_min >= area_xa and x_max <= area_xb
        
        # Check Y bounds (Reference uses inclusive bounds: >= and <=)
        is_in_y = y_min >= area_ya and y_max <= area_yb
        
        return is_in_x and is_in_y

    def guess_does_solve(self, level: EasyLevel) -> bool:
        """
        Translates the C++ fcsim_is_solved logic. 
        Checks for goal existence and ensures all goal pieces are in the area.
        """
        if not level.goal_pieces:
            return False
            
        for piece in level.goal_pieces:
            if not self._fcsim_in_area_check(piece, level):
                return False
                
        return True

# --- Variant 1: Mathematically Equivalent Commutative Swap (PR35Commutative) ---

class MathEquivalentPR35Commutative(PR35Reference):
    # ... (implementation remains the same)
    def _calculate_rotated_extents(self, w: float, h: float, angle_rad: float) -> tuple[float, float]:
        bex = w * 0.5
        bey = h * 0.5
        abs_cos_angle = abs(math.cos(angle_rad))
        abs_sin_angle = abs(math.sin(angle_rad))
        bex2 = (bey * abs_sin_angle) + (bex * abs_cos_angle)
        bey2 = (bey * abs_cos_angle) + (bex * abs_sin_angle)
        return bex2, bey2

# --- Variant 2: Associativity Test (PR35Fermi) ---

class PR35Fermi(PR35Reference):
    # ... (implementation remains the same)
    def _calculate_rotated_extents(self, w: float, h: float, angle_rad: float) -> tuple[float, float]:
        abs_cos_angle = abs(math.cos(angle_rad))
        abs_sin_angle = abs(math.sin(angle_rad))
        bex2_term1 = w * (0.5 * abs_cos_angle)
        bex2_term2 = h * (0.5 * abs_sin_angle)
        bex2 = bex2_term1 + bex2_term2
        bey2_term1 = w * (0.5 * abs_sin_angle)
        bey2_term2 = h * (0.5 * abs_cos_angle)
        bey2 = bey2_term1 + bey2_term2
        return bex2, bey2

# --- Variant 3: Boundary Strictness Test (PR35Gagarin) ---

class PR35Gagarin(PR35Reference):
    # ... (implementation remains the same)
    def _fcsim_in_area_check(self, piece, level: EasyLevel) -> bool:
        # Uses STICTLY exclusive bounds
        x, y, w, h, angle = piece['x'], piece['y'], piece['w'], piece['h'], piece['angle']
        area_x, area_y, area_w, area_h = level.goal_area_x, level.goal_area_y, level.goal_area_w, level.goal_area_h
        angle_rad = self._normalize_angle_for_check(angle)
        bex2, bey2 = self._calculate_rotated_extents(w, h, angle_rad)
        area_ex, area_ey = area_w * 0.5, area_h * 0.5
        area_xa, area_xb = area_x - area_ex, area_x + area_ex
        area_ya, area_yb = area_y - area_ey, area_y + area_ey
        x_min, x_max = x - bex2, x + bex2
        y_min, y_max = y - bey2, y + bey2
        is_in_x = x_min > area_xa and x_max < area_xb # STRICT
        is_in_y = y_min > area_ya and y_max < area_yb # STRICT
        return is_in_x and is_in_y

# --- Variant 4: Angle Normalization Multiplication Swap (PR35Salyut) ---

class PR35Salyut(PR35Reference):
    # ... (implementation remains the same)
    def _normalize_angle_for_check(self, angle: float) -> float:
        angle_deg = angle * RAD_TO_DEG
        if abs(angle_deg) >= DEGREE_CAP:
            angle_deg = -DEGREE_CAP
        return DEG_TO_RAD * angle_deg # Swapped order

# --- Variant 5: Containment Inequality Rearrangement (PR35Challenger) ---

class PR35Challenger(PR35Reference):
    # ... (implementation remains the same)
    def _fcsim_in_area_check(self, piece, level: EasyLevel) -> bool:
        x, y, w, h, angle = piece['x'], piece['y'], piece['w'], piece['h'], piece['angle']
        area_x, area_y, area_w, area_h = level.goal_area_x, level.goal_area_y, level.goal_area_w, level.goal_area_h
        angle_rad = self._normalize_angle_for_check(angle)
        bex2, bey2 = self._calculate_rotated_extents(w, h, angle_rad)
        area_ex, area_ey = area_w * 0.5, area_h * 0.5
        x_lower_check = (x + area_ex) >= (area_x + bex2)
        x_upper_check = (area_x + area_ex - x) >= bex2 
        y_lower_check = (y + area_ey) >= (area_y + bey2)
        y_upper_check = (area_y + area_ey - y) >= bey2
        is_in_x = x_lower_check and x_upper_check
        is_in_y = y_lower_check and y_upper_check
        return is_in_x and is_in_y
        
# --- Variant 6: Rearrangement of Goal Area Bounds (PR35Vostok) ---

class PR35Vostok(PR35Reference):
    # ... (implementation remains the same)
    def _fcsim_in_area_check(self, piece, level: EasyLevel) -> bool:
        x, y, w, h, angle = piece['x'], piece['y'], piece['w'], piece['h'], piece['angle']
        area_x, area_y, area_w, area_h = level.goal_area_x, level.goal_area_y, level.goal_area_w, level.goal_area_h
        angle_rad = self._normalize_angle_for_check(angle)
        bex2, bey2 = self._calculate_rotated_extents(w, h, angle_rad)
        # AREA CALCULATION REARRANGED HERE
        area_xa = (area_x * 2.0 - area_w) * 0.5
        area_xb = (area_x * 2.0 + area_w) * 0.5
        area_ya = (area_y * 2.0 - area_h) * 0.5
        area_yb = (area_y * 2.0 + area_h) * 0.5
        x_min, x_max = x - bex2, x + bex2
        y_min, y_max = y - bey2, y + bey2
        is_in_x = x_min >= area_xa and x_max <= area_xb
        is_in_y = y_min >= area_ya and y_max <= area_yb
        return is_in_x and is_in_y

# --- Variant 7: Distance-Based AABB Check (PR35Mercury) ---

class PR35Mercury(PR35Reference):
    # ... (implementation remains the same)
    def _fcsim_in_area_check(self, piece, level: EasyLevel) -> bool:
        x, y, w, h, angle = piece['x'], piece['y'], piece['w'], piece['h'], piece['angle']
        area_x, area_y, area_w, area_h = level.goal_area_x, level.goal_area_y, level.goal_area_w, level.goal_area_h
        angle_rad = self._normalize_angle_for_check(angle)
        bex2, bey2 = self._calculate_rotated_extents(w, h, angle_rad)
        area_ex, area_ey = area_w * 0.5, area_h * 0.5
        max_dist_x, max_dist_y = area_ex - bex2, area_ey - bey2
        dist_x, dist_y = abs(x - area_x), abs(y - area_y)
        is_in_x, is_in_y = dist_x <= max_dist_x, dist_y <= max_dist_y
        return is_in_x and is_in_y

# --- Variant 8: Quantization Hypothesis 1 - Round Rotated Extents (PR35Apollo) ---

class PR35Apollo(PR35Reference):
    """
    Rounds the final calculated Rotated Half-Extents (bex2, bey2) to the nearest multiple of 0.05.
    Uses _round_twip(..., mode=1) to preserve original 'nearest round' logic.
    """
    def _calculate_rotated_extents(self, w: float, h: float, angle_rad: float) -> tuple[float, float]:
        bex = w * 0.5
        bey = h * 0.5
        abs_cos_angle = abs(math.cos(angle_rad))
        abs_sin_angle = abs(math.sin(angle_rad))
        bex2_unrounded = (bex * abs_cos_angle) + (bey * abs_sin_angle)
        bey2_unrounded = (bex * abs_sin_angle) + (bey * abs_cos_angle)
        
        # Apply quantization (nearest round, mode=1)
        bex2 = _round_twip(bex2_unrounded, 1)
        bey2 = _round_twip(bey2_unrounded, 1)
        
        return bex2, bey2


# --- Variant 9: Quantization Hypothesis 2 - Round Piece Center (PR35Gemini) ---

class PR35Gemini(PR35Reference):
    """
    Rounds the Piece Center Coordinates (x, y) to the nearest multiple of 0.05.
    Uses _round_twip(..., mode=1) to preserve original 'nearest round' logic.
    """
    def _fcsim_in_area_check(self, piece, level: EasyLevel) -> bool:
        # Piece definition - QUANTIZATION APPLIED HERE (mode=1 for nearest round)
        x = _round_twip(piece['x'], 1)
        y = _round_twip(piece['y'], 1)
        w, h, angle = piece['w'], piece['h'], piece['angle']
        
        area_x, area_y, area_w, area_h = level.goal_area_x, level.goal_area_y, level.goal_area_w, level.goal_area_h
        
        angle_rad = self._normalize_angle_for_check(angle)
        bex2, bey2 = self._calculate_rotated_extents(w, h, angle_rad)
        area_ex, area_ey = area_w * 0.5, area_h * 0.5
        area_xa, area_xb = area_x - area_ex, area_x + area_ex
        area_ya, area_yb = area_y - area_ey, area_y + area_ey

        x_min, x_max = x - bex2, x + bex2
        y_min, y_max = y - bey2, y + bey2
        
        is_in_x = x_min >= area_xa and x_max <= area_xb
        is_in_y = y_min >= area_ya and y_max <= area_yb
        
        return is_in_x and is_in_y

# --- Variant 10: Quantization Hypothesis 3 - Round Initial Dimensions (PR35Saturn) ---

class PR35Saturn(PR35Reference):
    """
    Rounds the Piece Dimensions (w, h) to the nearest multiple of 0.05.
    Uses _round_twip(..., mode=1) to preserve original 'nearest round' logic.
    """
    def _calculate_rotated_extents(self, w: float, h: float, angle_rad: float) -> tuple[float, float]:
        # Dimensions are rounded before division/rotation (mode=1 for nearest round)
        w_rounded = _round_twip(w, 1)
        h_rounded = _round_twip(h, 1)
        
        bex = w_rounded * 0.5
        bey = h_rounded * 0.5
        
        abs_cos_angle = abs(math.cos(angle_rad))
        abs_sin_angle = abs(math.sin(angle_rad))
        
        bex2 = (bex * abs_cos_angle) + (bey * abs_sin_angle)
        bey2 = (bex * abs_sin_angle) + (bey * abs_cos_angle)
        
        return bex2, bey2

# --- Variant 11: Comprehensive Twip Quantization Tester (PR35TwipTester) ---

class PR35TwipTester(ParameterizedContestant):
    """
    Tests various quantization points using 5 rounding modes (none, round, floor, ceil, truncate).
    
    Discrete Parameters (10 total, each 0-4 mode):
    - Piece: W, H, X, Y
    - Area: W, H, X, Y
    - Rotated Extents: bex2, bey2
    """

    def __init__(self):
        super().__init__()
        # Define 10 discrete parameters, each controlling one rounding operation
        self.discrete_params = {
            'round_w': 0, 'round_h': 0,           # Piece Dimensions
            'round_x': 0, 'round_y': 0,           # Piece Position
            'round_area_w': 0, 'round_area_h': 0, # Area Dimensions
            'round_area_x': 0, 'round_area_y': 0, # Area Position
            'round_bex2': 0, 'round_bey2': 0      # Rotated Extents
        }
        self.ref = PR35Reference() # Use Reference's angle normalization
        self.mode_max = 4
    
    def adjust_time_budget(self, time_seconds):
        super().adjust_time_budget(time_seconds)
        self.mode_max = 4
        while self.mode_max > 1 and (self.mode_max + 1) ** 10 * 0.0002 > time_seconds:
            self.mode_max -= 1

    def get_discrete_param_bounds(self):
        """All 10 parameters are modes 0 to 4 (5 total modes)."""
        return {name: (0, self.mode_max) for name in self.discrete_params}

    def _calculate_rotated_extents(self, w: float, h: float, angle_rad: float) -> tuple[float, float]:
        """
        Calculates extents, applying rounding to initial dimensions and final extents.
        """
        # Apply rounding to initial piece dimensions
        w_rnd = _round_twip(w, self.discrete_params['round_w'])
        h_rnd = _round_twip(h, self.discrete_params['round_h'])
        
        # Piece half-extents (bex, bey in C++)
        bex = w_rnd * 0.5
        bey = h_rnd * 0.5
        
        abs_cos_angle = abs(math.cos(angle_rad))
        abs_sin_angle = abs(math.sin(angle_rad))
        
        # Reference calculation for unrounded rotated extents
        bex2_unrounded = (bex * abs_cos_angle) + (bey * abs_sin_angle)
        bey2_unrounded = (bex * abs_sin_angle) + (bey * abs_cos_angle)
        
        # Apply rounding to final rotated extents
        bex2 = _round_twip(bex2_unrounded, self.discrete_params['round_bex2'])
        bey2 = _round_twip(bey2_unrounded, self.discrete_params['round_bey2'])
        
        return bex2, bey2
        
    def _fcsim_in_area_check(self, piece, level: EasyLevel) -> bool:
        """
        Applies rounding to piece and area positions/dimensions before check.
        """
        # Piece definition (Apply position rounding)
        x = _round_twip(piece['x'], self.discrete_params['round_x'])
        y = _round_twip(piece['y'], self.discrete_params['round_y'])
        w, h, angle = piece['w'], piece['h'], piece['angle']
        
        # Area definition (Apply position and dimension rounding)
        area_x = _round_twip(level.goal_area_x, self.discrete_params['round_area_x'])
        area_y = _round_twip(level.goal_area_y, self.discrete_params['round_area_y'])
        area_w = _round_twip(level.goal_area_w, self.discrete_params['round_area_w'])
        area_h = _round_twip(level.goal_area_h, self.discrete_params['round_area_h'])
        
        # 1. Angle normalization (uses reference logic)
        angle_rad = self.ref._normalize_angle_for_check(angle)
        
        # 2. Rotated Half-Extents (Applies W/H and bex2/bey2 rounding internally)
        bex2, bey2 = self._calculate_rotated_extents(w, h, angle_rad)

        # 3. Calculate goal area bounds (area_xa, area_xb, area_ya, area_yb in C++)
        area_ex = area_w * 0.5
        area_ey = area_h * 0.5
        
        area_xa = area_x - area_ex
        area_xb = area_x + area_ex
        area_ya = area_y - area_ey
        area_yb = area_y + area_ey

        # 4. Final Containment Check (AABB vs AABB)
        x_min = x - bex2
        x_max = x + bex2
        y_min = y - bey2
        y_max = y + bey2
        
        # Reference uses inclusive bounds: >= and <=
        is_in_x = x_min >= area_xa and x_max <= area_xb
        is_in_y = y_min >= area_ya and y_max <= area_yb
        
        return is_in_x and is_in_y

    def guess_does_solve(self, level: EasyLevel) -> bool:
        if not level.goal_pieces:
            return False
            
        for piece in level.goal_pieces:
            if not self._fcsim_in_area_check(piece, level):
                return False
                
        return True

class PR35BoundaryTwipTester(ParameterizedContestant):
    """
    Focuses quantization on the piece's center, rotated half-extents, 
    and the four final calculated piece AABB boundaries (x_min, x_max, y_min, y_max).
    
    Discrete Parameters (8 total, each 0-4 mode):
    - Piece: X, Y (Center)
    - Rotated Half-Extents: bex2, bey2
    - Calculated AABB Bounds: x_min, x_max, y_min, y_max
    """

    def __init__(self):
        super().__init__()
        # Define 8 discrete parameters, each controlling one rounding operation
        self.discrete_params = {
            'round_x_center': 0, 'round_y_center': 0, # Piece Center Position
            'round_bex2': 0, 'round_bey2': 0,         # Rotated Extents
            'round_x_min': 0, 'round_x_max': 0,       # Calculated X Bounds
            'round_y_min': 0, 'round_y_max': 0        # Calculated Y Bounds
        }
        self.ref = PR35Reference() # Use Reference's angle normalization and base logic
        self.mode_max = 4
    
    def adjust_time_budget(self, time_seconds):
        super().adjust_time_budget(time_seconds)
        self.mode_max = 4
        while self.mode_max > 1 and (self.mode_max + 1) ** 8 * 0.0002 > time_seconds:
            self.mode_max -= 1

    def get_discrete_param_bounds(self):
        """All 8 parameters are modes 0 to 4 (5 total modes)."""
        return {name: (0, self.mode_max) for name in self.discrete_params}

    def _calculate_rotated_extents(self, w: float, h: float, angle_rad: float) -> tuple[float, float]:
        """
        Calculates extents, applying rounding ONLY to final bex2 and bey2.
        Uses original piece W/H without twipping.
        """
        bex = w * 0.5
        bey = h * 0.5
        
        abs_cos_angle = abs(math.cos(angle_rad))
        abs_sin_angle = abs(math.sin(angle_rad))
        
        # Reference calculation for unrounded rotated extents
        bex2_unrounded = (bex * abs_cos_angle) + (bey * abs_sin_angle)
        bey2_unrounded = (bex * abs_sin_angle) + (bey * abs_cos_angle)
        
        # Apply rounding to final rotated extents
        bex2 = _round_twip(bex2_unrounded, self.discrete_params['round_bex2'])
        bey2 = _round_twip(bey2_unrounded, self.discrete_params['round_bey2'])
        
        return bex2, bey2
        
    def _fcsim_in_area_check(self, piece, level: EasyLevel) -> bool:
        """
        Applies rounding to piece position and the four resulting AABB bounds.
        Area parameters are used as provided (no rounding).
        """
        # Piece definition - Apply position rounding
        x = _round_twip(piece['x'], self.discrete_params['round_x_center'])
        y = _round_twip(piece['y'], self.discrete_params['round_y_center'])
        w, h, angle = piece['w'], piece['h'], piece['angle']
        
        # Area definition - Used without rounding
        area_x, area_y = level.goal_area_x, level.goal_area_y
        area_w, area_h = level.goal_area_w, level.goal_area_h
        
        # 1. Angle normalization
        angle_rad = self.ref._normalize_angle_for_check(angle)
        
        # 2. Rotated Half-Extents (Applies bex2/bey2 rounding internally)
        bex2, bey2 = self._calculate_rotated_extents(w, h, angle_rad)

        # 3. Calculate goal area bounds
        area_ex = area_w * 0.5
        area_ey = area_h * 0.5
        area_xa = area_x - area_ex
        area_xb = area_x + area_ex
        area_ya = area_y - area_ey
        area_yb = area_y + area_ey

        # 4. Calculate Piece Bounds (Unrounded)
        x_min_unrounded = x - bex2
        x_max_unrounded = x + bex2
        y_min_unrounded = y - bey2
        y_max_unrounded = y + bey2
        
        # 5. Apply Quantization to Piece Bounds
        x_min = _round_twip(x_min_unrounded, self.discrete_params['round_x_min'])
        x_max = _round_twip(x_max_unrounded, self.discrete_params['round_x_max'])
        y_min = _round_twip(y_min_unrounded, self.discrete_params['round_y_min'])
        y_max = _round_twip(y_max_unrounded, self.discrete_params['round_y_max'])
        
        # 6. Final Containment Check
        # Reference uses inclusive bounds: >= and <=
        is_in_x = x_min >= area_xa and x_max <= area_xb
        is_in_y = y_min >= area_ya and y_max <= area_yb
        
        return is_in_x and is_in_y

    def guess_does_solve(self, level: EasyLevel) -> bool:
        if not level.goal_pieces:
            return False
            
        for piece in level.goal_pieces:
            if not self._fcsim_in_area_check(piece, level):
                return False
                
        return True


class PR35XTwipTester(ParameterizedContestant):
    """
    Tests quantization exclusively on X-axis related components.
    X_min and X_max boundaries share a single mode parameter.
    Y-axis twipping is completely disabled (mode 0).
    
    Discrete Parameters (3 total, each 0-4 mode):
    - mode_x_center: Rounds piece X.
    - mode_bex2: Rounds rotated half-extent BEX2.
    - mode_x_bounds: Rounds both x_min and x_max bounds.
    """

    def __init__(self):
        super().__init__()
        # Define 3 discrete parameters for X-axis twipping
        self.discrete_params = {
            'mode_x_center': 0,    # Piece Center Position X
            'mode_bex2': 0,        # Rotated Extent X
            'mode_x_bounds': 0     # Calculated X Bounds (x_min, x_max)
        }
        self.ref = PR35Reference() # Use Reference's angle normalization and base logic

    def get_discrete_param_bounds(self):
        """All 3 parameters are modes 0 to 4 (5 total modes)."""
        return {name: (0, 4) for name in self.discrete_params}

    def _calculate_rotated_extents(self, w: float, h: float, angle_rad: float) -> tuple[float, float]:
        """
        Calculates extents, applying rounding ONLY to final bex2 (X-axis).
        BEY2 (Y-axis) is not twipped.
        """
        bex = w * 0.5
        bey = h * 0.5
        
        abs_cos_angle = abs(math.cos(angle_rad))
        abs_sin_angle = abs(math.sin(angle_rad))
        
        # Reference calculation for unrounded rotated extents
        bex2_unrounded = (bex * abs_cos_angle) + (bey * abs_sin_angle)
        bey2_unrounded = (bex * abs_sin_angle) + (bey * abs_cos_angle)
        
        # Apply rounding to BEX2 (X-axis)
        bex2 = _round_twip(bex2_unrounded, self.discrete_params['mode_bex2'])
        
        # BEY2 (Y-axis) is NOT rounded (mode 0)
        bey2 = bey2_unrounded
        
        return bex2, bey2
        
    def _fcsim_in_area_check(self, piece, level: EasyLevel) -> bool:
        """
        Applies rounding to piece X position and the resulting X-AABB bounds.
        Y-axis values are not twipped.
        """
        # Piece definition - Apply rounding only to X position
        x = _round_twip(piece['x'], self.discrete_params['mode_x_center'])
        y = piece['y'] # Y is not twipped
        w, h, angle = piece['w'], piece['h'], piece['angle']
        
        # Area definition - Used without rounding
        area_x, area_y = level.goal_area_x, level.goal_area_y
        area_w, area_h = level.goal_area_w, level.goal_area_h
        
        # 1. Angle normalization
        angle_rad = self.ref._normalize_angle_for_check(angle)
        
        # 2. Rotated Half-Extents (BEX2 is twipped internally, BEY2 is not)
        bex2, bey2 = self._calculate_rotated_extents(w, h, angle_rad)

        # 3. Calculate goal area bounds
        area_ex = area_w * 0.5
        area_ey = area_h * 0.5
        area_xa = area_x - area_ex
        area_xb = area_x + area_ex
        area_ya = area_y - area_ey
        area_yb = area_y + area_ey
        
        # 4. Calculate Piece Bounds (Unrounded Y, Twipped X/BEX2)
        x_min_unrounded = x - bex2
        x_max_unrounded = x + bex2
        y_min = y - bey2 # Y is NOT twipped
        y_max = y + bey2 # Y is NOT twipped
        
        # 5. Apply Quantization to X Piece Bounds (using the shared mode)
        x_bound_mode = self.discrete_params['mode_x_bounds']
        x_min = _round_twip(x_min_unrounded, x_bound_mode)
        x_max = _round_twip(x_max_unrounded, x_bound_mode)
        
        # 6. Final Containment Check
        # Reference uses inclusive bounds: >= and <=
        is_in_x = x_min >= area_xa and x_max <= area_xb
        is_in_y = y_min >= area_ya and y_max <= area_yb
        
        return is_in_x and is_in_y

    def guess_does_solve(self, level: EasyLevel) -> bool:
        if not level.goal_pieces:
            return False
            
        for piece in level.goal_pieces:
            if not self._fcsim_in_area_check(piece, level):
                return False
                
        return True


# --- Variant: Combined Twip Quantization Tester (PR35CombinedTwipTester) ---

class PR35CombinedTwipTester(ParameterizedContestant):
    """
    Tests quantization across all relevant calculated values for both the piece
    and the area. Uses a grouped 6-parameter approach to keep the search space
    manageable (5^6 = 15,625 combinations).
    
    Discrete Parameters (6 total, each 0-4 mode):
    - mode_x_calc: Rounds piece X center and rotated half-extent BEX2.
    - mode_x_piece_bound: Rounds the final x_min and x_max piece boundaries.
    - mode_x_area_bound: Rounds the final area_xa and area_xb boundaries.
    - mode_y_calc: Rounds piece Y center and rotated half-extent BEY2.
    - mode_y_piece_bound: Rounds the final y_min and y_max piece boundaries.
    - mode_y_area_bound: Rounds the final area_ya and area_yb boundaries.
    """

    def __init__(self):
        super().__init__()
        # Define 6 discrete parameters
        self.discrete_params = {
            'mode_x_calc': 0,           # Piece X center and BEX2
            'mode_x_piece_bound': 0,    # Piece X min/max
            'mode_x_area_bound': 0,     # Area X a/b
            'mode_y_calc': 0,           # Piece Y center and BEY2
            'mode_y_piece_bound': 0,    # Piece Y min/max
            'mode_y_area_bound': 0      # Area Y a/b
        }
        self.ref = PR35Reference() 

    def get_discrete_param_bounds(self):
        """All 6 parameters are modes 0 to 4 (5 total modes)."""
        return {name: (0, 4) for name in self.discrete_params}

    def _calculate_rotated_extents(self, w: float, h: float, angle_rad: float) -> tuple[float, float]:
        """
        Calculates extents, applying rounding to BEX2 and BEY2 based on the calc modes.
        W/H are used without twipping.
        """
        bex = w * 0.5
        bey = h * 0.5
        
        abs_cos_angle = abs(math.cos(angle_rad))
        abs_sin_angle = abs(math.sin(angle_rad))
        
        # Reference calculation for unrounded rotated extents
        bex2_unrounded = (bex * abs_cos_angle) + (bey * abs_sin_angle)
        bey2_unrounded = (bex * abs_sin_angle) + (bey * abs_cos_angle)
        
        # Apply rounding to BEX2 and BEY2
        bex2 = _round_twip(bex2_unrounded, self.discrete_params['mode_x_calc'])
        bey2 = _round_twip(bey2_unrounded, self.discrete_params['mode_y_calc'])
        
        return bex2, bey2
        
    def _fcsim_in_area_check(self, piece, level: EasyLevel) -> bool:
        """
        Applies twipping to piece position, piece AABB bounds, and area AABB bounds.
        """
        # Piece definition - Apply rounding to X and Y position
        x = _round_twip(piece['x'], self.discrete_params['mode_x_calc'])
        y = _round_twip(piece['y'], self.discrete_params['mode_y_calc'])
        w, h, angle = piece['w'], piece['h'], piece['angle']
        
        # Area definition - Used without rounding
        area_x, area_y = level.goal_area_x, level.goal_area_y
        area_w, area_h = level.goal_area_w, level.goal_area_h
        
        # 1. Angle normalization
        angle_rad = self.ref._normalize_angle_for_check(angle)
        
        # 2. Rotated Half-Extents (BEX2/BEY2 are twipped internally)
        bex2, bey2 = self._calculate_rotated_extents(w, h, angle_rad)

        # 3. Calculate goal area bounds (Unrounded)
        area_ex = area_w * 0.5
        area_ey = area_h * 0.5
        area_xa_unrounded = area_x - area_ex
        area_xb_unrounded = area_x + area_ex
        area_ya_unrounded = area_y - area_ey
        area_yb_unrounded = area_y + area_ey

        # 3b. Apply Quantization to Area Bounds
        area_xa = _round_twip(area_xa_unrounded, self.discrete_params['mode_x_area_bound'])
        area_xb = _round_twip(area_xb_unrounded, self.discrete_params['mode_x_area_bound'])
        area_ya = _round_twip(area_ya_unrounded, self.discrete_params['mode_y_area_bound'])
        area_yb = _round_twip(area_yb_unrounded, self.discrete_params['mode_y_area_bound'])

        # 4. Calculate Piece Bounds (Unrounded)
        x_min_unrounded = x - bex2
        x_max_unrounded = x + bex2
        y_min_unrounded = y - bey2
        y_max_unrounded = y + bey2
        
        # 5. Apply Quantization to Piece Bounds
        x_min = _round_twip(x_min_unrounded, self.discrete_params['mode_x_piece_bound'])
        x_max = _round_twip(x_max_unrounded, self.discrete_params['mode_x_piece_bound'])
        y_min = _round_twip(y_min_unrounded, self.discrete_params['mode_y_piece_bound'])
        y_max = _round_twip(y_max_unrounded, self.discrete_params['mode_y_piece_bound'])
        
        # 6. Final Containment Check
        # Reference uses inclusive bounds: >= and <=
        is_in_x = x_min >= area_xa and x_max <= area_xb
        is_in_y = y_min >= area_ya and y_max <= area_yb
        
        return is_in_x and is_in_y

    def guess_does_solve(self, level: EasyLevel) -> bool:
        if not level.goal_pieces:
            return False
            
        for piece in level.goal_pieces:
            if not self._fcsim_in_area_check(piece, level):
                return False
                
        return True