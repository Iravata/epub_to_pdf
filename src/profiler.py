import time
import functools
from typing import Callable, Any
import cProfile
import pstats
import io

class PerformanceProfiler:
    """Profile and optimize performance (KISS)"""
    
    def __init__(self):
        self.timings = {}
    
    def time_function(self, func: Callable) -> Callable:
        """Decorator to time function execution"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start
            
            func_name = func.__name__
            if func_name not in self.timings:
                self.timings[func_name] = []
            
            self.timings[func_name].append(duration)
            
            return result
        
        return wrapper
    
    def profile_code(self, func: Callable) -> str:
        """Profile code execution"""
        profiler = cProfile.Profile()
        profiler.enable()
        
        # Run function
        func()
        
        profiler.disable()
        
        # Get stats
        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.sort_stats('cumulative')
        stats.print_stats(10)  # Top 10 functions
        
        return stream.getvalue()
    
    def get_report(self) -> str:
        """Get performance report"""
        report = ["Performance Report", "=" * 50]
        
        for func_name, times in self.timings.items():
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            
            report.append(f"\n{func_name}:")
            report.append(f"  Average: {avg_time:.3f}s")
            report.append(f"  Min: {min_time:.3f}s")
            report.append(f"  Max: {max_time:.3f}s")
            report.append(f"  Calls: {len(times)}")
        
        return '\n'.join(report)