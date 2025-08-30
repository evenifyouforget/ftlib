"""Core data structures and utilities for Spacelight Tournament"""

import ast
import inspect
import math
import textwrap
from abc import ABC, abstractmethod
from collections import namedtuple
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


def count_ast_nodes(func) -> int:
    """Count AST nodes in a function to measure complexity"""
    try:
        source = inspect.getsource(func)
        # Remove leading indentation to fix IndentationError
        dedented_source = textwrap.dedent(source)
        tree = ast.parse(dedented_source)
        return sum(1 for _ in ast.walk(tree))
    except Exception:
        return 0  # Return 0 if AST analysis fails


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def get_pass_rate_color(pass_rate: float) -> str:
    """Get color for pass rate using 6-bracket system"""
    if pass_rate >= 0.95: return Colors.BRIGHT_GREEN
    elif pass_rate >= 0.85: return Colors.GREEN  
    elif pass_rate >= 0.70: return Colors.YELLOW
    elif pass_rate >= 0.50: return Colors.BRIGHT_YELLOW
    elif pass_rate >= 0.25: return Colors.RED
    else: return Colors.BRIGHT_RED


def get_complexity_color(ast_nodes: int) -> str:
    """Get color for AST complexity using 6-bracket system"""
    if ast_nodes >= 150: return Colors.BRIGHT_RED
    elif ast_nodes >= 100: return Colors.RED
    elif ast_nodes >= 75: return Colors.BRIGHT_YELLOW
    elif ast_nodes >= 50: return Colors.YELLOW
    elif ast_nodes >= 25: return Colors.GREEN
    else: return Colors.BRIGHT_GREEN


@dataclass
class EasyLevel:
    """Represents a level for goal rectangle testing"""
    design_id: str
    url: str
    goal_area_x: float
    goal_area_y: float
    goal_area_w: float
    goal_area_h: float
    goal_area_angle: float
    goal_pieces: List[Dict[str, Any]]
    expected_result: Optional[bool] = None


class Contestant(ABC):
    """Abstract base class for goal rectangle checking contestants"""
    
    @abstractmethod
    def guess_does_solve(self, level: EasyLevel) -> bool:
        """Predict whether the design solves the level"""
        pass


class ParameterizedContestant(Contestant):
    """Base class for contestants with tunable parameters"""
    
    def __init__(self):
        self.params = {}
    
    @abstractmethod
    def get_param_bounds(self) -> Dict[str, tuple]:
        """Return parameter bounds for optimization"""
        pass
    
    def set_params(self, params: Dict[str, float]):
        """Set parameter values"""
        self.params = params