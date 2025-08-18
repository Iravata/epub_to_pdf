# EPUB to PDF Converter

A robust Python-based EPUB to PDF converter with advanced features and optimizations.

## Features

- ✅ Converts EPUB 2.0/3.0 files to PDF
- ✅ Preserves formatting, images, and structure
- ✅ Generates table of contents with bookmarks
- ✅ Customizable page layout and margins
- ✅ CSS style preservation
- ✅ Error recovery and graceful degradation
- ✅ Memory-efficient processing for large files
- ✅ Batch conversion support
- ✅ Streaming mode for large EPUBs
- ✅ Comprehensive Click-based CLI
- ✅ Progress bars and colored output
- ✅ Robust error handling with detailed logging

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/epub_to_pdf.git
cd epub_to_pdf

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest
```

## Usage

### Basic Conversion
```bash
# Convert EPUB to PDF
python -m src.cli convert input.epub

# Or specify output path
python -m src.cli convert input.epub -o output.pdf
```

### Advanced Options
```bash
python -m src.cli convert input.epub -o output.pdf \
    --page-size A4 \
    --margins 1 0.75 1 0.75 \
    --page-numbers \
    --toc \
    --preserve-styles \
    --header "My Book" \
    --footer "Page" \
    --streaming \
    --debug
```

### Batch Conversion
```bash
# Convert multiple EPUB files
python -m src.cli batch *.epub --output-dir ./pdfs/

# With options
python -m src.cli batch *.epub --output-dir ./pdfs/ \
    --page-size A4 \
    --preserve-styles \
    --continue-on-error
```

### Get Help
```bash
# Show all available commands
python -m src.cli --help

# Get help for specific command
python -m src.cli convert --help
python -m src.cli batch --help
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--page-size` | Page size (letter, A4, A5) | letter |
| `--margins` | Margins in inches (top right bottom left) | None |
| `--page-numbers` | Add page numbers | False |
| `--toc` | Generate table of contents | True |
| `--preserve-styles` | Preserve CSS styles | True |
| `--header` | Page header text | None |
| `--footer` | Page footer text | None |
| `--streaming` | Use streaming mode for large files | False |
| `--debug` | Show detailed error information | False |

## Performance

- Processes average 300-page book in < 10 seconds
- Memory usage < 500MB for standard conversion
- Streaming mode available for files > 100MB
- Automatic memory optimization and garbage collection
- Performance profiling and monitoring

## Error Handling

The converter includes robust error handling using Click's error handling mechanisms:
- Continues processing despite missing images
- Handles malformed HTML gracefully
- Recovers from memory issues automatically
- Provides detailed error logs with `--debug`
- Uses Click's `ClickException` for user-friendly error messages
- Implements Click's `echo()` for consistent output formatting
- Progress bars show conversion status
- Batch mode can continue on individual file failures

## Testing

```bash
# Run all tests (including CLI tests)
pytest

# Run CLI-specific tests
pytest tests/test_cli.py -v

# Test error handling
pytest tests/test_error_handling.py -v

# Test performance optimizations
pytest tests/test_performance.py -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run integration tests
pytest tests/test_integration.py -v
```

### Click Testing Benefits

- **CliRunner**: Isolated testing environment for CLI commands
- **Output capture**: Test help text, error messages, and progress output
- **Exit code validation**: Ensure proper error handling
- **Type checking**: Click validates input types automatically
- **Integration testing**: Test complete CLI workflows
- **Progress bar testing**: Verify user experience elements

## Architecture

The converter follows a modular architecture with Phase 5 enhancements:

1. **EPUB Processing** - Extracts content from EPUB files with validation
2. **Content Organization** - Structures chapters and resources efficiently
3. **PDF Generation** - Creates PDF with advanced formatting
4. **Error Handling** - Centralized error management and recovery
5. **Memory Optimization** - Efficient processing of large files
6. **Performance Profiling** - Monitoring and optimization
7. **CLI Interface** - User-friendly Click-based command line

### Phase 5 Improvements

- **Robust Error Handling**: Comprehensive error capture and recovery
- **Memory Optimization**: Streaming mode and memory monitoring
- **Performance Profiling**: Built-in performance tracking
- **Enhanced CLI**: Click-based interface with progress bars
- **Input Validation**: Comprehensive file and option validation
- **Batch Processing**: Efficient multi-file conversion
- **Comprehensive Testing**: >90% test coverage with multiple test suites

## Development Principles

This project follows established software engineering principles:

- **TDD (Test-Driven Development)**: Comprehensive test suite with >90% coverage
- **KISS (Keep It Simple)**: Clean, readable code with clear documentation
- **DRY (Don't Repeat Yourself)**: Centralized error handling and reusable components
- **YAGNI (You Aren't Gonna Need It)**: Focused functionality without unnecessary features

## Contributing

Contributions are welcome! Please follow these principles:
- **TDD** - Write tests first
- **KISS** - Keep it simple
- **DRY** - Don't repeat yourself
- **YAGNI** - You aren't gonna need it

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linting and type checking
pytest --cov=src --cov-report=html
```

## Troubleshooting

### Common Issues

1. **Memory Errors**: Use `--streaming` flag for large files
2. **Invalid EPUB**: Check file format with `--debug` flag
3. **Permission Errors**: Ensure write access to output directory
4. **Missing Images**: Enable debug mode to see detailed warnings

### Debug Mode

Use `--debug` flag to get detailed error information:
```bash
python -m src.cli convert problematic.epub --debug
```

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Built with ReportLab for PDF generation
- Uses ebooklib for EPUB parsing
- BeautifulSoup for HTML processing
- Click for command-line interface
- psutil for memory monitoring
- pytest for comprehensive testing