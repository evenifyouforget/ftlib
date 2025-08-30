"""Tournament execution and main logic"""

import inspect
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from .core import Contestant, ParameterizedContestant, EasyLevel, Colors, count_ast_nodes, get_pass_rate_color, get_complexity_color
from .contestants import *
from .optimization import autotune_contestant
from .data_loading import load_easy_levels_from_tsv


class SpaceLightTournament:
    """Tournament for testing goal rectangle checking algorithms"""
    
    def __init__(self, easy_levels: List[EasyLevel]):
        self.easy_levels = easy_levels
        self.contestants = self._discover_contestants()
        
    def _discover_contestants(self) -> List[Contestant]:
        """Automatically discover all Contestant subclasses"""
        contestants = []
        
        # Get all classes from contestants module
        import spacelight.contestants as contestants_module
        for name, obj in inspect.getmembers(contestants_module):
            if (inspect.isclass(obj) and 
                issubclass(obj, Contestant) and 
                obj != Contestant and 
                obj != ParameterizedContestant and
                not name.startswith('_')):
                try:
                    contestant = obj()
                    contestants.append(contestant)
                except Exception as e:
                    print(f"⚠️  Could not instantiate {name}: {e}")
        
        return contestants
    
    def run_tournament(self, autotune_time: float = 60) -> Dict[str, Any]:
        """Run the tournament and return results"""
        print(f"🏁 {Colors.BOLD}SPACELIGHT TOURNAMENT - Generation 5 TDD Checker Research{Colors.RESET}")
        print(f"🎯 Testing {len(self.contestants)} contestants on {len(self.easy_levels)} levels")
        print()
        
        results = []
        
        for contestant in self.contestants:
            contestant_name = contestant.__class__.__name__
            
            # Auto-tune parameterized contestants
            if isinstance(contestant, ParameterizedContestant):
                print(f"🔧 {Colors.CYAN}Auto-tuning {contestant_name}...{Colors.RESET}")
                contestant = autotune_contestant(contestant, self.easy_levels, autotune_time)
                print()
            
            print(f"🧪 Testing {Colors.BOLD}{contestant_name}{Colors.RESET}...")
            
            correct_predictions = 0
            total_predictions = 0
            start_time = time.time()
            
            for level in self.easy_levels:
                if level.expected_result is not None:
                    try:
                        prediction = contestant.guess_does_solve(level)
                        if prediction == level.expected_result:
                            correct_predictions += 1
                        total_predictions += 1
                    except Exception as e:
                        print(f"   ❌ Error on level {level.design_id}: {e}")
            
            execution_time = time.time() - start_time
            pass_rate = correct_predictions / total_predictions if total_predictions > 0 else 0
            
            # Get function complexity
            ast_nodes = count_ast_nodes(contestant.guess_does_solve)
            ast_display = f"{ast_nodes}" if ast_nodes > 0 else "N/A"
            
            # Apply colors
            pass_rate_color = get_pass_rate_color(pass_rate)
            complexity_color = get_complexity_color(ast_nodes)
            
            print(f"   📊 Pass rate: {pass_rate_color}{pass_rate:.3f}{Colors.RESET} ({correct_predictions}/{total_predictions})")
            print(f"   ⚡ Complexity: {complexity_color}{ast_display} AST nodes{Colors.RESET}")
            print(f"   ⏱️  Time: {execution_time:.4f}s")
            
            if isinstance(contestant, ParameterizedContestant):
                print(f"   🎛️  Final params: {contestant.params}")
            
            print()
            
            results.append({
                'name': contestant_name,
                'pass_rate': pass_rate,
                'correct': correct_predictions,
                'total': total_predictions,
                'execution_time': execution_time,
                'ast_nodes': ast_nodes,
                'params': getattr(contestant, 'params', None)
            })
        
        # Print summary
        results.sort(key=lambda x: x['pass_rate'], reverse=True)
        
        print(f"🏆 {Colors.BOLD}TOURNAMENT RESULTS{Colors.RESET}")
        print(f"{'Rank':<4} {'Contestant':<35} {'Pass Rate':<12} {'Complexity':<12} {'Time':<8}")
        print("─" * 75)
        
        for i, result in enumerate(results, 1):
            name = result['name']
            pass_rate = result['pass_rate']
            ast_nodes = result['ast_nodes']
            exec_time = result['execution_time']
            
            pass_rate_color = get_pass_rate_color(pass_rate)
            complexity_color = get_complexity_color(ast_nodes)
            ast_display = f"{ast_nodes}" if ast_nodes > 0 else "N/A"
            
            print(f"{i:<4} {name:<35} {pass_rate_color}{pass_rate:.3f}{Colors.RESET}        {complexity_color}{ast_display:<8}{Colors.RESET}     {exec_time:.3f}s")
        
        tournament_results = {
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'total_contestants': len(self.contestants),
            'total_levels': len(self.easy_levels),
            'level_details': [
                {
                    'design_id': level.design_id,
                    'expected_result': level.expected_result,
                    'url': level.url
                } for level in self.easy_levels
            ],
            'dataset_stats': {
                'solve_count': sum(1 for l in self.easy_levels if l.expected_result == True),
                'fail_count': sum(1 for l in self.easy_levels if l.expected_result == False),
                'unknown_count': sum(1 for l in self.easy_levels if l.expected_result is None)
            }
        }
        
        # Save tournament log
        log_dir = Path(__file__).parent.parent / "tournament_logs"
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"spacelight_tournament_{timestamp}.json"
        
        with open(log_file, 'w') as f:
            json.dump(tournament_results, f, indent=2)
        
        print(f"\n💾 Tournament results saved to: {log_file}")
        
        return tournament_results