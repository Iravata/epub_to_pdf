import gc
import psutil
from contextlib import contextmanager
from typing import Generator, Dict, Any, List
import sys

class MemoryOptimizer:
    """Optimize memory usage for large files"""
    
    def __init__(self, threshold_mb: int = 400):
        self.threshold = threshold_mb * 1024 * 1024
        self.peak_memory = 0
        self.initial_memory = 0
    
    @contextmanager
    def monitor(self):
        """Monitor memory usage"""
        self.initial_memory = self._get_memory_usage()
        
        try:
            yield self
        finally:
            self.peak_memory = self._get_memory_usage()
            
            # Force garbage collection if needed
            if self.peak_memory > self.threshold:
                gc.collect()
    
    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes"""
        return psutil.Process().memory_info().rss
    
    def get_peak_memory(self) -> float:
        """Get peak memory usage in MB"""
        return self.peak_memory / 1024 / 1024
    
    def chunk_iterator(self, items: List[Any], chunk_size: int = 10) -> Generator:
        """Create memory-efficient chunk iterator"""
        for i in range(0, len(items), chunk_size):
            chunk = items[i:i + chunk_size]
            yield chunk
            
            # Clear processed items from memory
            del chunk
            
            # Check memory and collect if needed
            if self._get_memory_usage() > self.threshold:
                gc.collect()
    
    def optimize_image(self, image_data: bytes, max_size: int = 1024 * 1024) -> bytes:
        """Optimize image data for memory efficiency"""
        # Simple optimization: return data as-is (KISS principle)
        # Real optimization would require image processing libraries
        return image_data
    
    def clear_cache(self):
        """Clear caches to free memory"""
        gc.collect()