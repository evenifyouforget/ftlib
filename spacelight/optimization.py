"""Optimization and auto-tuning functionality"""

import time
import numpy as np
from scipy import optimize
from typing import List, Dict

from .core import ParameterizedContestant, EasyLevel, Colors


def autotune_contestant(contestant: ParameterizedContestant, 
                       easy_levels: List[EasyLevel], 
                       max_time_seconds: float = 60) -> ParameterizedContestant:
    """Autotune a parameterized contestant using adaptive interleaved hybrid optimization"""
    print(f"🔧 Auto-tuning {contestant.__class__.__name__} for {max_time_seconds}s...")
    
    # Calculate initial pass rate
    initial_correct = 0
    initial_total = 0
    for level in easy_levels:
        if level.expected_result is not None:
            prediction = contestant.guess_does_solve(level)
            if prediction == level.expected_result:
                initial_correct += 1
            initial_total += 1
    
    initial_pass_rate = initial_correct / initial_total if initial_total > 0 else 0
    initial_params = contestant.params.copy()
    
    print(f"📊 Initial: {initial_params}")
    print(f"📈 Initial pass rate: {initial_pass_rate:.4f} ({initial_correct}/{initial_total})")
    
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
    
    try:
        # Adaptive interleaved hybrid optimization
        def time_remaining():
            return max(0, max_time_seconds - (time.time() - start_time))
        
        best_result = None
        best_score = float('inf')
        best_x = initial_guess.copy()
        
        # Track per-algorithm performance
        algorithm_stats = {
            'differential_evolution': {'improvements': 0, 'time_spent': 0},
            'basin_hopping': {'improvements': 0, 'time_spent': 0},
            'lbfgs_b': {'improvements': 0, 'time_spent': 0},
            'nelder_mead': {'improvements': 0, 'time_spent': 0}
        }
        
        print(f"🔧 {Colors.BOLD}Adaptive Interleaved Hybrid Optimization{Colors.RESET}")
        
        # Algorithm pool with adaptive time slices
        algorithms = [
            ('differential_evolution', 0.3),  # Initial time allocation
            ('basin_hopping', 0.25),
            ('lbfgs_b', 0.25), 
            ('nelder_mead', 0.2)
        ]
        
        iteration = 0
        min_slice_time = 0.1  # Minimum time slice per algorithm
        
        while time_remaining() > min_slice_time and iteration < 100:
            iteration += 1
            
            # Adaptive time allocation based on past performance
            if iteration > 1:
                total_improvements = sum(stats['improvements'] for stats in algorithm_stats.values())
                if total_improvements > 0:
                    # Reallocate time based on success rates
                    new_allocations = []
                    for algo_name, _ in algorithms:
                        success_rate = algorithm_stats[algo_name]['improvements'] / max(1, iteration)
                        # Base allocation + bonus for successful algorithms
                        allocation = 0.1 + 0.9 * (success_rate / max(0.01, total_improvements / len(algorithms)))
                        new_allocations.append((algo_name, allocation))
                    
                    # Normalize allocations
                    total_alloc = sum(alloc for _, alloc in new_allocations)
                    algorithms = [(name, alloc/total_alloc) for name, alloc in new_allocations]
            
            # Run each algorithm for its allocated time slice
            for algo_name, time_fraction in algorithms:
                if time_remaining() < min_slice_time:
                    break
                
                slice_time = min(time_remaining() * time_fraction, time_remaining() - min_slice_time * (len(algorithms) - 1))
                if slice_time < min_slice_time:
                    continue
                
                algo_start = time.time()
                previous_best = best_score
                
                print(f"🎯 Iteration {iteration}: {algo_name} ({slice_time:.1f}s, {time_remaining():.1f}s total remaining)")
                
                try:
                    if algo_name == 'differential_evolution':
                        # Short burst of DE with early termination
                        def de_callback(xk, convergence):
                            return time.time() - algo_start >= slice_time
                        
                        result = optimize.differential_evolution(
                            objective_function,
                            param_bounds,
                            x0=best_x,
                            maxiter=min(100, int(slice_time * 50)),  # Scale iterations with time
                            popsize=min(15, max(4, len(param_bounds) * 2)),  # Adaptive population
                            callback=de_callback,
                            polish=False  # Skip final polish to save time
                        )
                    
                    elif algo_name == 'basin_hopping':
                        # Basin hopping with time limit
                        def bh_callback(x, f, accepted):
                            return time.time() - algo_start < slice_time
                        
                        result = optimize.basinhopping(
                            objective_function,
                            best_x,
                            niter=max(1, int(slice_time * 5)),  # Scale iterations with time
                            T=0.1,  # Temperature for acceptance
                            stepsize=0.1,  # Step size for random displacement
                            callback=bh_callback,
                            minimizer_kwargs={
                                'method': 'L-BFGS-B',
                                'bounds': param_bounds,
                                'options': {'maxiter': 10}  # Quick local search
                            }
                        )
                    
                    elif algo_name == 'lbfgs_b':
                        # Multiple L-BFGS-B starts with different perturbations
                        best_local = None
                        best_local_score = float('inf')
                        
                        num_starts = max(1, int(slice_time * 10))  # More starts for longer time
                        for start_idx in range(num_starts):
                            if time.time() - algo_start >= slice_time:
                                break
                            
                            # Random perturbation around best point
                            noise_scale = 0.1 * (1 - start_idx / num_starts)  # Decrease noise over time
                            x0_perturbed = best_x + np.random.normal(0, noise_scale, size=len(best_x))
                            for i, (low, high) in enumerate(param_bounds):
                                x0_perturbed[i] = np.clip(x0_perturbed[i], low, high)
                            
                            local_result = optimize.minimize(
                                objective_function,
                                x0_perturbed,
                                method='L-BFGS-B',
                                bounds=param_bounds,
                                options={'maxiter': max(10, int((slice_time - (time.time() - algo_start)) * 100))}
                            )
                            
                            if local_result.fun < best_local_score:
                                best_local = local_result
                                best_local_score = local_result.fun
                        
                        result = best_local
                    
                    elif algo_name == 'nelder_mead':
                        # Nelder-Mead with adaptive parameters
                        # Convert bounds to unconstrained problem for NM
                        def bounded_objective(x_bounded):
                            # Map from [0,1] to actual bounds
                            x_actual = []
                            for i, (low, high) in enumerate(param_bounds):
                                x_actual.append(low + x_bounded[i] * (high - low))
                            return objective_function(x_actual)
                        
                        # Convert best_x to [0,1] space
                        x0_normalized = []
                        for i, (low, high) in enumerate(param_bounds):
                            x0_normalized.append((best_x[i] - low) / (high - low))
                        
                        max_iterations = max(10, int(slice_time * 20))
                        result_nm = optimize.minimize(
                            bounded_objective,
                            x0_normalized,
                            method='Nelder-Mead',
                            options={'maxiter': max_iterations, 'adaptive': True}
                        )
                        
                        # Convert back to actual bounds
                        if result_nm.success:
                            x_actual = []
                            for i, (low, high) in enumerate(param_bounds):
                                x_actual.append(low + result_nm.x[i] * (high - low))
                            result = type('Result', (), {
                                'x': np.array(x_actual),
                                'fun': result_nm.fun,
                                'success': result_nm.success
                            })()
                        else:
                            result = result_nm
                    
                    # Update statistics and best result
                    elapsed_time = time.time() - algo_start
                    algorithm_stats[algo_name]['time_spent'] += elapsed_time
                    
                    if result and hasattr(result, 'fun') and result.fun < best_score:
                        algorithm_stats[algo_name]['improvements'] += 1
                        best_score = result.fun
                        best_x = result.x.copy()
                        best_result = result
                        improvement = previous_best - result.fun
                        print(f"   ✅ {algo_name}: New best! Score: {-best_score:.4f} (improved by {improvement:.4f})")
                    else:
                        print(f"   🔄 {algo_name}: No improvement (best remains {-best_score:.4f})")
                
                except Exception as e:
                    print(f"   ❌ {algo_name}: Error - {e}")
                    algorithm_stats[algo_name]['time_spent'] += time.time() - algo_start
        
        # Print final statistics
        print(f"\n📊 {Colors.BOLD}Algorithm Performance Summary{Colors.RESET}:")
        for algo_name, stats in algorithm_stats.items():
            efficiency = stats['improvements'] / max(1, stats['time_spent'])
            print(f"   {algo_name}: {stats['improvements']} improvements in {stats['time_spent']:.2f}s (eff: {efficiency:.2f}/s)")
        
        result = best_result
        
        if result.success:
            optimized_params = dict(zip(param_names, result.x))
            contestant.set_params(optimized_params)
            
            # Calculate final pass rate
            final_correct = 0
            final_total = 0
            for level in easy_levels:
                if level.expected_result is not None:
                    prediction = contestant.guess_does_solve(level)
                    if prediction == level.expected_result:
                        final_correct += 1
                    final_total += 1
            
            final_pass_rate = final_correct / final_total if final_total > 0 else 0
            
            elapsed_time = time.time() - start_time
            efficiency = (elapsed_time / max_time_seconds) * 100
            
            print(f"📊 Final: {optimized_params}")
            print(f"📈 Final pass rate: {final_pass_rate:.4f} ({final_correct}/{final_total})")
            print(f"⏱️  Total time: {elapsed_time:.2f}s (efficiency: {efficiency:.1f}%)")
            print(f"🎯 Improvement: {final_pass_rate - initial_pass_rate:.4f}")
            
        else:
            print(f"❌ Optimization failed: {result.message if hasattr(result, 'message') else 'Unknown error'}")
            
    except Exception as e:
        print(f"❌ Auto-tuning failed: {e}")
    
    return contestant