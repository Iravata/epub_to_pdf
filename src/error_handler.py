import logging
from contextlib import contextmanager
from typing import List, Optional
from pathlib import Path
import traceback

class ConversionError(Exception):
    """Custom exception for conversion errors"""
    pass

class ErrorHandler:
    """Simplified centralized error handling"""
    
    def __init__(self, log_file: Optional[str] = None):
        self.errors = []
        self.warnings = []
        self.memory_warnings = 0
        
        # Setup logging
        self.logger = logging.getLogger('epub_to_pdf')
        self.logger.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    @contextmanager
    def capture_errors(self):
        """Context manager for error capture"""
        try:
            yield self
        except ConversionError as e:
            self.log_error(f"Conversion error: {e}")
            raise
        except MemoryError as e:
            self.memory_warnings += 1
            self.log_warning(f"Memory warning: {e}")
            # Try to recover
            import gc
            gc.collect()
        except Exception as e:
            self.log_error(f"Unexpected error: {e}")
            self.log_error(traceback.format_exc())
    
    def log_error(self, message: str):
        """Log an error"""
        self.errors.append(message)
        self.logger.error(message)
    
    def log_warning(self, message: str):
        """Log a warning"""
        self.warnings.append(message)
        self.logger.warning(message)
    
    def log_info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def has_errors(self) -> bool:
        """Check if errors occurred"""
        return bool(self.errors)
    
    def has_warnings(self) -> bool:
        """Check if warnings occurred"""
        return bool(self.warnings)
    
    def get_error_count(self) -> int:
        """Get number of errors"""
        return len(self.errors)
    
    
    def get_warnings(self) -> List[str]:
        """Get warning messages"""
        return self.warnings
    
    def get_memory_warnings(self) -> int:
        """Get number of memory warnings"""
        return self.memory_warnings
    
    def clear(self):
        """Clear all errors and warnings"""
        self.errors.clear()
        self.warnings.clear()
        self.memory_warnings = 0
    
    def get_summary(self) -> str:
        """Get error summary"""
        summary = []
        
        if self.errors:
            summary.append(f"Errors: {len(self.errors)}")
            for error in self.errors[:3]:  # Show first 3
                summary.append(f"  - {error}")
        
        if self.warnings:
            summary.append(f"Warnings: {len(self.warnings)}")
            for warning in self.warnings[:3]:
                summary.append(f"  - {warning}")
        
        return '\n'.join(summary) if summary else "No errors or warnings"