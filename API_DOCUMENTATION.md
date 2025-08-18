# API Documentation

## Core Classes

### OptimizedEPUBProcessor

Enhanced EPUB processor with error handling and performance optimizations.

```python
from src.optimized_converter import OptimizedEPUBProcessor

# Basic usage
processor = OptimizedEPUBProcessor("book.epub")
result = processor.process()

# Streaming mode for large files
processor = OptimizedEPUBProcessor("large_book.epub", streaming=True)
result = processor.process()
```

#### Constructor Parameters

- `epub_path` (str): Path to the EPUB file
- `streaming` (bool, optional): Enable streaming mode for large files. Default: False

#### Methods

- `process()` → Dict[str, Any]: Process entire EPUB file with error handling
- `process_streaming()` → Generator: Process EPUB in streaming chunks
- `get_performance_report()` → str: Get performance profiling report

#### Properties

- `error_handler`: ErrorHandler instance for logging and error management
- `memory_optimizer`: MemoryOptimizer instance for memory efficiency
- `profiler`: PerformanceProfiler instance for performance tracking

### EnhancedPDFGenerator

Generate PDF from processed EPUB data with advanced features.

```python
from src.enhanced_pdf_generator import EnhancedPDFGenerator

generator = EnhancedPDFGenerator("output.pdf", options={
    'page_numbers': True,
    'preserve_styles': True,
    'margins': {'top': 1, 'right': 1, 'bottom': 1, 'left': 1},
    'header': 'Book Title',
    'footer': 'Page'
})

success = generator.generate(epub_data)
```

#### Constructor Parameters

- `output_path` (str): Path for output PDF file
- `options` (Dict[str, Any], optional): Generation options

#### Methods

- `generate(epub_data)` → bool: Generate PDF from EPUB data
- `set_page_size(size)` → None: Set page size ('letter', 'A4', 'A5')
- `set_metadata(metadata)` → None: Set PDF metadata

### ErrorHandler

Centralized error handling with logging capabilities.

```python
from src.error_handler import ErrorHandler

# Basic usage
handler = ErrorHandler()

# With file logging
handler = ErrorHandler(log_file="conversion.log")

# Context manager usage
with handler.capture_errors():
    # Your code here
    pass
```

#### Constructor Parameters

- `log_file` (Optional[str]): Path to log file for error logging

#### Methods

- `log_error(message)` → None: Log an error message
- `log_warning(message)` → None: Log a warning message
- `log_info(message)` → None: Log an info message
- `has_errors()` → bool: Check if errors occurred
- `has_warnings()` → bool: Check if warnings occurred
- `get_error_count()` → int: Get number of errors
- `get_warnings()` → List[str]: Get warning messages
- `get_memory_warnings()` → int: Get number of memory warnings
- `clear()` → None: Clear all errors and warnings
- `get_summary()` → str: Get formatted error summary

#### Context Manager

- `capture_errors()`: Context manager for automatic error capture and recovery

### InputValidator

Comprehensive input validation and sanitization.

```python
from src.validator import InputValidator

validator = InputValidator()

# Validate EPUB file
is_valid, error_msg = validator.validate_epub("book.epub")

# Validate output path
is_valid = validator.validate_output_path("output.pdf")

# Sanitize filename
clean_name = validator.sanitize_filename("my/book?.pdf")  # → "my_book_.pdf"
```

#### Methods

- `validate_epub(epub_path)` → Tuple[bool, Optional[str]]: Comprehensive EPUB validation
- `validate_output_path(output_path)` → bool: Validate and prepare output path
- `validate_file_size(file_path, size)` → bool: Check file size limits
- `validate_options(options)` → bool: Validate conversion options
- `sanitize_filename(filename)` → str: Clean filename for filesystem compatibility

### MemoryOptimizer

Memory usage optimization for large file processing.

```python
from src.memory_optimizer import MemoryOptimizer

optimizer = MemoryOptimizer(threshold_mb=400)

# Monitor memory usage
with optimizer.monitor():
    # Memory-intensive operations
    pass

peak_memory = optimizer.get_peak_memory()  # in MB
```

#### Constructor Parameters

- `threshold_mb` (int): Memory threshold in MB for optimization triggers. Default: 400

#### Methods

- `monitor()`: Context manager for memory monitoring
- `get_peak_memory()` → float: Get peak memory usage in MB
- `chunk_iterator(items, chunk_size=10)` → Generator: Memory-efficient chunk processing
- `optimize_image(image_data, max_size=1MB)` → bytes: Optimize image data
- `clear_cache()` → None: Clear system caches to free memory

### PerformanceProfiler

Performance monitoring and profiling.

```python
from src.profiler import PerformanceProfiler

profiler = PerformanceProfiler()

# Decorator for timing functions
@profiler.time_function
def my_function():
    # Function implementation
    pass

# Generate performance report
report = profiler.get_report()
```

#### Methods

- `time_function(func)` → Callable: Decorator for function timing
- `profile_code(func)` → str: Profile function execution with cProfile
- `get_report()` → str: Generate formatted performance report

## Usage Examples

### Basic Conversion

```python
from src.optimized_converter import OptimizedEPUBProcessor
from src.enhanced_pdf_generator import EnhancedPDFGenerator

# Process EPUB with error handling
processor = OptimizedEPUBProcessor("book.epub")
epub_data = processor.process()

# Generate PDF with advanced options
options = {
    'page_numbers': True,
    'preserve_styles': True,
    'margins': {'top': 1, 'right': 0.75, 'bottom': 1, 'left': 0.75}
}

generator = EnhancedPDFGenerator("output.pdf", options)
success = generator.generate(epub_data)

if success:
    print("Conversion successful!")
else:
    print("Conversion failed")
```

### Streaming Large Files

```python
from src.optimized_converter import OptimizedEPUBProcessor

# Enable streaming mode for large files
processor = OptimizedEPUBProcessor("large_book.epub", streaming=True)
result = processor.process()

if result['_streaming']:
    # Process chunks one by one
    for chunk in result['_generator']:
        if 'metadata' in chunk:
            print(f"Metadata: {chunk['metadata']['title']}")
        elif 'chapters' in chunk:
            print(f"Processing {len(chunk['chapters'])} chapters")
        elif 'image' in chunk:
            print(f"Processing image: {chunk['image']['name']}")
```

### Error Handling and Logging

```python
from src.error_handler import ErrorHandler
from src.optimized_converter import OptimizedEPUBProcessor

# Setup logging to file
handler = ErrorHandler(log_file="conversion.log")

try:
    with handler.capture_errors():
        processor = OptimizedEPUBProcessor("problematic.epub")
        epub_data = processor.process()
        
        # Check for warnings/errors
        if processor.error_handler.has_errors():
            print("Errors occurred during processing:")
            print(processor.error_handler.get_summary())
        
except Exception as e:
    print(f"Conversion failed: {e}")
    print(f"Total errors: {handler.get_error_count()}")
```

### Performance Monitoring

```python
from src.optimized_converter import OptimizedEPUBProcessor
from src.memory_optimizer import MemoryOptimizer

# Monitor memory and performance
processor = OptimizedEPUBProcessor("book.epub")

with processor.memory_optimizer.monitor():
    epub_data = processor.process()

print(f"Peak memory usage: {processor.memory_optimizer.get_peak_memory():.1f} MB")
print("Performance report:")
print(processor.get_performance_report())
```

### Batch Processing

```python
from src.optimized_converter import OptimizedEPUBProcessor
from src.enhanced_pdf_generator import EnhancedPDFGenerator
from pathlib import Path

epub_files = list(Path(".").glob("*.epub"))
results = []

for epub_file in epub_files:
    try:
        processor = OptimizedEPUBProcessor(str(epub_file))
        epub_data = processor.process()
        
        output_file = epub_file.with_suffix('.pdf')
        generator = EnhancedPDFGenerator(str(output_file))
        success = generator.generate(epub_data)
        
        results.append({
            'file': epub_file.name,
            'success': success,
            'errors': processor.error_handler.get_error_count()
        })
        
    except Exception as e:
        results.append({
            'file': epub_file.name,
            'success': False,
            'error': str(e)
        })

# Summary
successful = sum(1 for r in results if r['success'])
print(f"Batch conversion: {successful}/{len(results)} files converted")
```

### Input Validation

```python
from src.validator import InputValidator

validator = InputValidator()

# Validate before processing
epub_files = ["book1.epub", "book2.epub", "invalid.txt"]

for file in epub_files:
    is_valid, error_msg = validator.validate_epub(file)
    if is_valid:
        print(f"✅ {file} is valid")
    else:
        print(f"❌ {file}: {error_msg}")

# Validate options
options = {
    'page_size': 'A4',
    'margins': [1, 1, 1, 1]
}

if validator.validate_options(options):
    print("Options are valid")
else:
    print("Invalid options")
```

## Error Types

### ConversionError

Custom exception for conversion-specific errors.

```python
from src.error_handler import ConversionError

try:
    # Conversion code
    pass
except ConversionError as e:
    print(f"Conversion error: {e}")
```

### Click Exceptions

The CLI uses Click's exception system for user-friendly error messages:

- `click.ClickException`: General CLI errors
- `click.BadParameter`: Invalid parameter values
- `click.FileError`: File-related errors

## Configuration

### Memory Optimization Settings

```python
# Adjust memory threshold (default: 400MB)
optimizer = MemoryOptimizer(threshold_mb=200)

# Adjust chunk size for streaming (default: 10)
for chunk in optimizer.chunk_iterator(items, chunk_size=5):
    # Process smaller chunks
    pass
```

### Validation Limits

```python
# Current limits in InputValidator
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
VALID_PAGE_SIZES = ['letter', 'A4', 'A5']
```

## Extension Points

The API is designed for extensibility:

### Custom Error Handlers

```python
class CustomErrorHandler(ErrorHandler):
    def log_error(self, message: str):
        # Custom error handling logic
        super().log_error(message)
        # Send to external logging service
```

### Custom Validators

```python
class CustomValidator(InputValidator):
    def validate_epub(self, epub_path: str):
        # Custom validation logic
        base_valid, base_error = super().validate_epub(epub_path)
        
        # Additional custom checks
        return base_valid, base_error
```

### Performance Plugins

```python
class CustomProfiler(PerformanceProfiler):
    def get_report(self) -> str:
        # Custom report format
        base_report = super().get_report()
        return f"Custom Report:\n{base_report}"
```