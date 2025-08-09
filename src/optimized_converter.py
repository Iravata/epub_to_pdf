"""Optimized EPUB converter with all improvements"""

from pathlib import Path
from typing import Dict, Any, Generator, Optional
import gc

from .converter import EPUBProcessor
from .error_handler import ErrorHandler
from .validator import InputValidator
from .memory_optimizer import MemoryOptimizer
from .profiler import PerformanceProfiler

class OptimizedEPUBProcessor(EPUBProcessor):
    """Optimized EPUB processor with error handling and performance improvements"""
    
    def __init__(self, epub_path: str, streaming: bool = False):
        # Initialize error handler
        self.error_handler = ErrorHandler()
        
        # Validate input
        validator = InputValidator()
        is_valid, error_msg = validator.validate_epub(epub_path)
        
        if not is_valid:
            self.error_handler.log_error(error_msg)
            raise ValueError(error_msg)
        
        # Initialize optimizer and profiler
        self.memory_optimizer = MemoryOptimizer()
        self.profiler = PerformanceProfiler()
        
        # Streaming mode for large files
        self.streaming = streaming
        
        # Initialize parent with error handling
        try:
            super().__init__(epub_path)
        except Exception as e:
            self.error_handler.log_error(f"Initialization error: {e}")
            raise
    
    def process(self) -> Dict[str, Any]:
        """Process EPUB with optimization and error handling"""
        with self.error_handler.capture_errors():
            with self.memory_optimizer.monitor():
                if self.streaming:
                    # Return generator for streaming
                    return self._create_streaming_result()
                else:
                    # Normal processing with optimizations
                    return self._process_optimized()
    
    def process_streaming(self) -> Generator[Dict[str, Any], None, None]:
        """Process EPUB in streaming mode for large files"""
        with self.error_handler.capture_errors():
            # Parse metadata first
            metadata = self.metadata_parser.parse()
            yield {'metadata': metadata}
            
            # Stream chapters in chunks
            chapters = self.content_organizer.get_chapters()
            
            for chunk in self.memory_optimizer.chunk_iterator(chapters, 10):
                yield {'chapters': chunk}
                
                # Clear memory after each chunk
                gc.collect()
            
            # Stream other components
            yield {'toc': self.navigation_parser.parse_toc()}
            
            # Stream images one by one
            images = self.resource_handler.get_images()
            for image in images:
                # Optimize image memory
                image['data'] = self.memory_optimizer.optimize_image(image['data'])
                yield {'image': image}
    
    def _process_optimized(self) -> Dict[str, Any]:
        """Optimized normal processing with consolidated error handling"""
        result = {}
        
        # Process components with unified error recovery
        result['metadata'] = self._process_with_fallback(
            lambda: self.metadata_parser.parse(),
            "Metadata parsing error",
            self._get_default_metadata(),
            log_as_warning=True
        )
        
        result['chapters'] = self._process_with_fallback(
            lambda: self.content_organizer.get_chapters(),
            "Chapter extraction error",
            [],
            log_as_warning=False
        )
        
        result['structure'] = self._process_with_fallback(
            lambda: self.content_organizer.get_structure(),
            "Structure parsing error", 
            {'type': 'book', 'children': result['chapters']},
            log_as_warning=True
        )
        
        result['toc'] = self._process_with_fallback(
            lambda: self.navigation_parser.parse_toc(),
            "TOC parsing error",
            [],
            log_as_warning=True
        )
        
        # Handle images with optimization
        def process_images():
            images = self.resource_handler.get_images()
            if len(images) > 50:
                self.error_handler.log_info(f"Optimizing {len(images)} images")
                for image in images:
                    image['data'] = self.memory_optimizer.optimize_image(image['data'])
            return images
            
        result['images'] = self._process_with_fallback(
            process_images,
            "Image extraction error",
            [],
            log_as_warning=True
        )
        
        result['styles'] = self._process_with_fallback(
            lambda: self.resource_handler.get_stylesheets(),
            "Stylesheet extraction error",
            [],
            log_as_warning=True
        )
        
        # Add error summary to result
        result['_errors'] = self.error_handler.get_summary()
        
        return result
    
    def _create_streaming_result(self) -> Dict[str, Any]:
        """Create a result dict that indicates streaming mode"""
        return {
            '_streaming': True,
            '_generator': self.process_streaming()
        }
    
    def _process_with_fallback(self, operation, error_msg: str, fallback_value, log_as_warning: bool = True):
        """Execute operation with standardized error handling and fallback"""
        try:
            return operation()
        except Exception as e:
            full_msg = f"{error_msg}: {e}"
            if log_as_warning:
                self.error_handler.log_warning(full_msg)
            else:
                self.error_handler.log_error(full_msg)
            return fallback_value
    
    def _get_default_metadata(self) -> Dict[str, Any]:
        """Get default metadata when parsing fails"""
        return {
            'title': 'Unknown Title',
            'author': 'Unknown Author',
            'language': 'en',
            'description': ''
        }
    
    def get_performance_report(self) -> str:
        """Get performance profiling report"""
        return self.profiler.get_report()