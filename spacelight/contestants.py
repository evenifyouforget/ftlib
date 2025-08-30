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


class FCBehaviorBaselineContestant(Contestant):
    """Mimics some observed behaviors from original FC implementation"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        for piece in level.goal_pieces:
            x, y = piece['x'], piece['y']
            w, h = piece['w'], piece['h']
            angle = piece['angle']
            
            area_x, area_y = level.goal_area_x, level.goal_area_y
            area_w, area_h = level.goal_area_w, level.goal_area_h
            area_angle = level.goal_area_angle
            
            # Apply some quirky transformations that might match FC behavior
            effective_angle = angle % (2 * math.pi)
            if effective_angle > math.pi:
                effective_angle -= 2 * math.pi
            
            # Basic bounding box check with small tolerance
            tolerance = 0.1
            if (area_x - area_w/2 - tolerance <= x <= area_x + area_w/2 + tolerance and
                area_y - area_h/2 - tolerance <= y <= area_y + area_h/2 + tolerance):
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


class CenterDistanceContestant(Contestant):
    """Checks if piece center is close enough to goal area center"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        for piece in level.goal_pieces:
            piece_center_x, piece_center_y = piece['x'], piece['y']
            goal_center_x, goal_center_y = level.goal_area_x, level.goal_area_y
            
            distance = math.sqrt((piece_center_x - goal_center_x)**2 + (piece_center_y - goal_center_y)**2)
            threshold = min(level.goal_area_w, level.goal_area_h) / 2
            
            if distance <= threshold:
                return True
        
        return False


class BoundingBoxContestant(Contestant):
    """Uses axis-aligned bounding box overlap"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        for piece in level.goal_pieces:
            piece_x, piece_y = piece['x'], piece['y']
            piece_w, piece_h = piece['w'], piece['h']
            
            # Piece bounding box
            piece_left = piece_x - piece_w/2
            piece_right = piece_x + piece_w/2
            piece_bottom = piece_y - piece_h/2
            piece_top = piece_y + piece_h/2
            
            # Goal area bounding box
            goal_left = level.goal_area_x - level.goal_area_w/2
            goal_right = level.goal_area_x + level.goal_area_w/2
            goal_bottom = level.goal_area_y - level.goal_area_h/2
            goal_top = level.goal_area_y + level.goal_area_h/2
            
            # Check overlap
            if (piece_left < goal_right and piece_right > goal_left and
                piece_bottom < goal_top and piece_top > goal_bottom):
                return True
        
        return False


class AngleIgnoreContestant(Contestant):
    """Ignores rotation completely"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        for piece in level.goal_pieces:
            x, y = piece['x'], piece['y']
            w, h = piece['w'], piece['h']
            
            area_x, area_y = level.goal_area_x, level.goal_area_y
            area_w, area_h = level.goal_area_w, level.goal_area_h
            
            if (area_x - area_w/2 <= x <= area_x + area_w/2 and
                area_y - area_h/2 <= y <= area_y + area_h/2):
                return True
        
        return False


class ModuloAngleContestant(Contestant):
    """Uses modulo operations on angles"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        for piece in level.goal_pieces:
            x, y = piece['x'], piece['y']
            w, h = piece['w'], piece['h']
            angle = piece['angle']
            
            area_x, area_y = level.goal_area_x, level.goal_area_y
            area_w, area_h = level.goal_area_w, level.goal_area_h
            
            # Normalize angle to [0, 2π]
            normalized_angle = angle % (2 * math.pi)
            
            # Simple rotation check with normalized angle
            cos_a, sin_a = math.cos(normalized_angle), math.sin(normalized_angle)
            half_w, half_h = w / 2, h / 2
            
            corners = [
                (x + cos_a * half_w - sin_a * half_h, y + sin_a * half_w + cos_a * half_h),
                (x - cos_a * half_w - sin_a * half_h, y - sin_a * half_w + cos_a * half_h),
                (x + cos_a * half_w + sin_a * half_h, y + sin_a * half_w - cos_a * half_h),
                (x - cos_a * half_w + sin_a * half_h, y - sin_a * half_w - cos_a * half_h)
            ]
            
            area_xa, area_ya = area_x - area_w/2, area_y - area_h/2
            area_xb, area_yb = area_x + area_w/2, area_y + area_h/2
            
            all_in_bounds = True
            for corner_x, corner_y in corners:
                if not (area_xa <= corner_x <= area_xb and area_ya <= corner_y <= area_yb):
                    all_in_bounds = False
                    break
            
            if all_in_bounds:
                return True
        
        return False


class QuantizedAngleContestant(Contestant):
    """Quantizes angles to specific steps"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        for piece in level.goal_pieces:
            x, y = piece['x'], piece['y']
            w, h = piece['w'], piece['h']
            angle = piece['angle']
            
            area_x, area_y = level.goal_area_x, level.goal_area_y
            area_w, area_h = level.goal_area_w, level.goal_area_h
            
            # Quantize angle to nearest 0.1 radian
            quantized_angle = round(angle / 0.1) * 0.1
            
            cos_a, sin_a = math.cos(quantized_angle), math.sin(quantized_angle)
            half_w, half_h = w / 2, h / 2
            
            corners = [
                (x + cos_a * half_w - sin_a * half_h, y + sin_a * half_w + cos_a * half_h),
                (x - cos_a * half_w - sin_a * half_h, y - sin_a * half_w + cos_a * half_h),
                (x + cos_a * half_w + sin_a * half_h, y + sin_a * half_w - cos_a * half_h),
                (x - cos_a * half_w + sin_a * half_h, y - sin_a * half_w - cos_a * half_h)
            ]
            
            area_xa, area_ya = area_x - area_w/2, area_y - area_h/2
            area_xb, area_yb = area_x + area_w/2, area_y + area_h/2
            
            all_in_bounds = True
            for corner_x, corner_y in corners:
                if not (area_xa <= corner_x <= area_xb and area_ya <= corner_y <= area_yb):
                    all_in_bounds = False
                    break
            
            if all_in_bounds:
                return True
        
        return False


class ExtremeAngleClampContestant(Contestant):
    """Clamps angles to extreme values"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        for piece in level.goal_pieces:
            x, y = piece['x'], piece['y']
            w, h = piece['w'], piece['h']
            angle = piece['angle']
            
            area_x, area_y = level.goal_area_x, level.goal_area_y
            area_w, area_h = level.goal_area_w, level.goal_area_h
            
            # Extreme clamping: limit to [-π/4, π/4]
            clamped_angle = max(-math.pi/4, min(math.pi/4, angle))
            
            cos_a, sin_a = math.cos(clamped_angle), math.sin(clamped_angle)
            half_w, half_h = w / 2, h / 2
            
            corners = [
                (x + cos_a * half_w - sin_a * half_h, y + sin_a * half_w + cos_a * half_h),
                (x - cos_a * half_w - sin_a * half_h, y - sin_a * half_w + cos_a * half_h),
                (x + cos_a * half_w + sin_a * half_h, y + sin_a * half_w - cos_a * half_h),
                (x - cos_a * half_w + sin_a * half_h, y - sin_a * half_w - cos_a * half_h)
            ]
            
            area_xa, area_ya = area_x - area_w/2, area_y - area_h/2
            area_xb, area_yb = area_x + area_w/2, area_y + area_h/2
            
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


class FtlibNoRotationContestant(Contestant):
    """Ftlib logic but ignoring rotation"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        for piece in level.goal_pieces:
            x, y = piece['x'], piece['y']
            w, h = piece['w'], piece['h']
            
            area_x, area_y = level.goal_area_x, level.goal_area_y
            area_w, area_h = level.goal_area_w, level.goal_area_h
            
            # Simple axis-aligned check (no rotation)
            piece_xa = x - w / 2
            piece_xb = x + w / 2
            piece_ya = y - h / 2
            piece_yb = y + h / 2
            
            area_xa = area_x - area_w / 2
            area_xb = area_x + area_w / 2
            area_ya = area_y - area_h / 2
            area_yb = area_y + area_h / 2
            
            if (piece_xa >= area_xa and piece_xb <= area_xb and
                piece_ya >= area_ya and piece_yb <= area_yb):
                return True
        
        return False


class FtlibBoundingBoxContestant(Contestant):
    """Uses ftlib logic with bounding box approximation"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        for piece in level.goal_pieces:
            x, y = piece['x'], piece['y']
            w, h = piece['w'], piece['h']
            angle = piece['angle']
            
            area_x, area_y = level.goal_area_x, level.goal_area_y
            area_w, area_h = level.goal_area_w, level.goal_area_h
            
            # Calculate axis-aligned bounding box of rotated piece
            cos_a, sin_a = abs(math.cos(angle)), abs(math.sin(angle))
            bbox_w = w * cos_a + h * sin_a
            bbox_h = w * sin_a + h * cos_a
            
            # Check if bounding box fits in goal area
            if (area_x - area_w/2 <= x - bbox_w/2 and x + bbox_w/2 <= area_x + area_w/2 and
                area_y - area_h/2 <= y - bbox_h/2 and y + bbox_h/2 <= area_y + area_h/2):
                return True
        
        return False


class FtlibWithClampingContestant(Contestant):
    """Ftlib logic with angle clamping"""
    
    def guess_does_solve(self, level: EasyLevel) -> bool:
        for piece in level.goal_pieces:
            x, y = piece['x'], piece['y']
            w, h = piece['w'], piece['h']
            angle = piece['angle']
            
            area_x, area_y = level.goal_area_x, level.goal_area_y
            area_w, area_h = level.goal_area_w, level.goal_area_h
            
            # Clamp angle to reasonable range
            clamped_angle = max(-math.pi, min(math.pi, angle))
            
            # Calculate goal area bounds
            area_xa = area_x - area_w / 2
            area_xb = area_x + area_w / 2
            area_ya = area_y - area_h / 2
            area_yb = area_y + area_h / 2
            
            # Calculate piece extents
            bex = w / 2
            bey = h / 2
            
            # Calculate rotated corner offsets with clamped angle
            x0 = math.cos(clamped_angle) * bex
            y0 = math.sin(clamped_angle) * bex
            x1 = math.sin(clamped_angle) * bey
            y1 = -math.cos(clamped_angle) * bey
            
            # Check all 4 corners are in bounds
            corners = [
                (x + x0 + x1, y + y0 + y1),
                (x - x0 + x1, y - y0 + y1),
                (x + x0 - x1, y + y0 - y1),
                (x - x0 - x1, y - y0 - y1),
            ]
            
            for xx, yy in corners:
                if xx < area_xa or xx > area_xb or yy < area_ya or yy > area_yb:
                    return False
            
            return True
        
        return False