import pytest
from click.testing import CliRunner
from src.cli import main, convert, batch
import tempfile
from pathlib import Path

class TestCLI:
    def setup_method(self):
        """Set up test fixtures"""
        self.runner = CliRunner()
    
    def test_main_shows_help_without_subcommand(self):
        """Test main command shows help when no subcommand provided"""
        result = self.runner.invoke(main, [])
        assert result.exit_code == 0
        assert "EPUB to PDF Converter" in result.output
    
    def test_convert_requires_input_file(self):
        """Test convert command requires input file argument"""
        result = self.runner.invoke(convert, [])
        assert result.exit_code == 2  # Click exits with 2 for missing arguments
        assert "Missing argument" in result.output
    
    def test_convert_validates_file_existence(self):
        """Test convert command validates input file exists"""
        result = self.runner.invoke(convert, ['nonexistent.epub'])
        assert result.exit_code == 2
        assert "does not exist" in result.output
    
    def test_convert_with_valid_options(self):
        """Test convert command accepts valid options"""
        with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as tmp_epub:
            epub_path = Path(tmp_epub.name)
            # Create a minimal EPUB structure for testing
            tmp_epub.write(b'PK\x03\x04')  # ZIP signature
        
        try:
            # This will fail during processing but should parse arguments correctly
            result = self.runner.invoke(convert, [
                str(epub_path),
                '--page-size', 'A4',
                '--page-numbers',
                '--debug'
            ])
            # Should not exit with argument parsing error (exit code 2)
            assert result.exit_code != 2
        finally:
            epub_path.unlink(missing_ok=True)
    
    def test_batch_requires_input_files(self):
        """Test batch command requires input files"""
        result = self.runner.invoke(batch, [])
        assert result.exit_code == 2
        assert "Missing argument" in result.output
    
    def test_convert_margin_validation(self):
        """Test convert command validates margin parameters"""
        with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as tmp_epub:
            epub_path = Path(tmp_epub.name)
            tmp_epub.write(b'PK\x03\x04')
        
        try:
            # Test negative margins
            result = self.runner.invoke(convert, [
                str(epub_path),
                '--margins', '-1', '1', '1', '1'
            ])
            assert result.exit_code != 0
            assert "Margins must be non-negative" in result.output
            
            # Test excessive margins
            result = self.runner.invoke(convert, [
                str(epub_path),
                '--margins', '6', '1', '1', '1'
            ])
            assert result.exit_code != 0
            assert "Margins cannot exceed 5 inches" in result.output
        finally:
            epub_path.unlink(missing_ok=True)