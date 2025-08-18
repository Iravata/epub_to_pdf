import pytest
from pathlib import Path
from click.testing import CliRunner
from src.error_handler import ErrorHandler, ConversionError
from src.optimized_converter import OptimizedEPUBProcessor
from src.cli import main

class TestErrorHandling:
    def test_handle_corrupt_epub(self, tmp_path):
        """Test handling of corrupted EPUB files"""
        # Create a corrupt EPUB (not a valid ZIP)
        corrupt_epub = tmp_path / "corrupt.epub"
        corrupt_epub.write_text("This is not a valid EPUB file")
        
        handler = ErrorHandler()
        
        with pytest.raises(ValueError, match="Invalid EPUB format"):
            OptimizedEPUBProcessor(str(corrupt_epub))
    
    def test_handle_missing_file(self):
        """Test handling of missing EPUB files"""
        handler = ErrorHandler()
        
        with pytest.raises(ValueError, match="File not found"):
            OptimizedEPUBProcessor("nonexistent.epub")
    
    def test_cli_error_handling(self):
        """Test CLI error handling with Click"""
        runner = CliRunner()
        
        # Test invalid file
        result = runner.invoke(main, ['nonexistent.epub', 'output.pdf'])
        assert result.exit_code != 0
        assert 'not found' in result.output.lower() or 'error' in result.output.lower()
    
    def test_cli_invalid_output_path(self):
        """Test CLI with invalid output path"""
        runner = CliRunner()
        
        # Create a temporary EPUB file
        with runner.isolated_filesystem():
            Path("test.epub").write_text("test")
            
            # Test invalid output path (not .pdf extension)
            result = runner.invoke(main, ['test.epub', 'output.txt'])
            assert result.exit_code != 0
    
    def test_error_logging(self, tmp_path):
        """Test error logging to file"""
        log_file = tmp_path / "errors.log"
        handler = ErrorHandler(log_file=str(log_file))
        
        handler.log_error("Test error")
        handler.log_warning("Test warning")
        
        assert log_file.exists()
        content = log_file.read_text()
        assert "Test error" in content
        assert "Test warning" in content
    
    def test_error_handler_context_manager(self):
        """Test error handler context manager"""
        handler = ErrorHandler()
        
        with handler.capture_errors():
            handler.log_error("Test error in context")
        
        assert handler.has_errors()
        assert handler.get_error_count() == 1
        assert "Test error in context" in handler.errors
    
    def test_error_handler_memory_warnings(self):
        """Test memory warning handling"""
        handler = ErrorHandler()
        
        # Simulate memory warning
        try:
            with handler.capture_errors():
                raise MemoryError("Out of memory")
        except MemoryError:
            pass  # Expected to be caught and handled
        
        assert handler.get_memory_warnings() == 1
        assert handler.has_warnings()
    
    def test_error_summary(self):
        """Test error summary generation"""
        handler = ErrorHandler()
        
        handler.log_error("Error 1")
        handler.log_error("Error 2")
        handler.log_warning("Warning 1")
        
        summary = handler.get_summary()
        assert "Errors: 2" in summary
        assert "Warnings: 1" in summary
        assert "Error 1" in summary
        assert "Warning 1" in summary
    
    def test_error_handler_clear(self):
        """Test clearing errors and warnings"""
        handler = ErrorHandler()
        
        handler.log_error("Test error")
        handler.log_warning("Test warning")
        
        assert handler.has_errors()
        assert handler.has_warnings()
        
        handler.clear()
        
        assert not handler.has_errors()
        assert not handler.has_warnings()
        assert handler.get_error_count() == 0