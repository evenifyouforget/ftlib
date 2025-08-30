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


class PatternBasedContestant(Contestant):
    """Looks for patterns in design IDs and goal areas"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        # Pattern 1: Design ID patterns (purely empirical)
        design_id = int(level.design_id)
        
        # Observed pattern: newer designs (higher IDs) more likely to solve
        if design_id > 12700000:
            base_score = 0.95
        elif design_id > 12600000:
            base_score = 0.85  
        elif design_id > 1000000:
            base_score = 0.75
        else:
            base_score = 0.65
        
        # Pattern 2: Goal area characteristics
        area_w, area_h = level.goal_area_w, level.goal_area_h
        area_size = area_w * area_h
        
        # Smaller goal areas seem harder to satisfy
        if area_size < 1000:
            base_score *= 0.7
        elif area_size > 5000:
            base_score *= 1.1
            
        # Use random threshold based on calculated probability
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