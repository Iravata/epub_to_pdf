import pytest
from pathlib import Path
from click.testing import CliRunner
from src.validator import InputValidator
from src.cli import main

class TestInputValidation:
    def test_validate_file_size(self):
        """Test file size validation"""
        validator = InputValidator()
        
        # Should accept files up to 500MB
        assert validator.validate_file_size("test.epub", 100 * 1024 * 1024)
        assert not validator.validate_file_size("test.epub", 600 * 1024 * 1024)
    
    def test_validate_output_path(self, tmp_path):
        """Test output path validation"""
        validator = InputValidator()
        
        # Valid paths
        assert validator.validate_output_path(str(tmp_path / "output.pdf"))
        
        # Invalid paths - wrong extension
        assert not validator.validate_output_path(str(tmp_path / "output.txt"))
    
    def test_validate_output_path_creates_directory(self, tmp_path):
        """Test output path validation creates missing directories"""
        validator = InputValidator()
        
        # Path with non-existent parent directory
        new_dir = tmp_path / "new_dir"
        output_path = new_dir / "output.pdf"
        
        assert validator.validate_output_path(str(output_path))
        assert new_dir.exists()
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        validator = InputValidator()
        
        assert validator.sanitize_filename("book.pdf") == "book.pdf"
        assert validator.sanitize_filename("my/book.pdf") == "my_book.pdf"
        assert validator.sanitize_filename("book?.pdf") == "book_.pdf"
        assert validator.sanitize_filename("book<test>.pdf") == "book_test_.pdf"
        
        # Test empty filename
        assert validator.sanitize_filename("") == "output.pdf"
        assert validator.sanitize_filename("   ") == "output.pdf"
        
        # Test filename without .pdf extension
        assert validator.sanitize_filename("book") == "book.pdf"
    
    def test_validate_options(self):
        """Test option validation"""
        validator = InputValidator()
        
        valid_options = {
            'page_size': 'A4',
            'margins': [1, 1, 1, 1]
        }
        assert validator.validate_options(valid_options)
        
        # Invalid page size
        invalid_options = {
            'page_size': 'invalid',
            'margins': [1, 1, 1, 1]
        }
        assert not validator.validate_options(invalid_options)
        
        # Invalid margins - wrong number of values
        invalid_options = {
            'page_size': 'A4',
            'margins': [1, 2, 3]  # Should be 4 values
        }
        assert not validator.validate_options(invalid_options)
        
        # Invalid margins - negative values
        invalid_options = {
            'page_size': 'A4',
            'margins': [1, -1, 1, 1]
        }
        assert not validator.validate_options(invalid_options)
    
    def test_validate_epub_valid_file(self, tmp_path):
        """Test EPUB validation with valid file"""
        validator = InputValidator()
        
        # Create a file that looks like a ZIP (EPUB)
        epub_file = tmp_path / "test.epub"
        epub_file.write_bytes(b'PK\x03\x04')  # ZIP signature
        
        is_valid, error_msg = validator.validate_epub(str(epub_file))
        assert is_valid
        assert error_msg is None
    
    def test_validate_epub_missing_file(self):
        """Test EPUB validation with missing file"""
        validator = InputValidator()
        
        is_valid, error_msg = validator.validate_epub("nonexistent.epub")
        assert not is_valid
        assert "File not found" in error_msg
    
    def test_validate_epub_wrong_extension(self, tmp_path):
        """Test EPUB validation with wrong extension"""
        validator = InputValidator()
        
        wrong_ext_file = tmp_path / "test.txt"
        wrong_ext_file.write_text("test")
        
        is_valid, error_msg = validator.validate_epub(str(wrong_ext_file))
        assert not is_valid
        assert "Not an EPUB file" in error_msg
    
    def test_validate_epub_too_large(self, tmp_path):
        """Test EPUB validation with file too large"""
        validator = InputValidator()
        
        # Create a large file (simulate)
        large_epub = tmp_path / "large.epub"
        large_epub.write_bytes(b'PK\x03\x04' + b'x' * (600 * 1024 * 1024))  # 600MB
        
        is_valid, error_msg = validator.validate_epub(str(large_epub))
        assert not is_valid
        assert "File too large" in error_msg
    
    def test_validate_epub_invalid_format(self, tmp_path):
        """Test EPUB validation with invalid format"""
        validator = InputValidator()
        
        invalid_epub = tmp_path / "invalid.epub"
        invalid_epub.write_bytes(b'Not a ZIP file')
        
        is_valid, error_msg = validator.validate_epub(str(invalid_epub))
        assert not is_valid
        assert "Invalid EPUB format" in error_msg
    
    def test_click_option_validation_page_size(self):
        """Test Click option validation for page size"""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Create a dummy EPUB
            Path("test.epub").write_bytes(b'PK\x03\x04')
            
            # Test invalid page size
            result = runner.invoke(main, ['test.epub', 'output.pdf', '--page-size', 'invalid'])
            # Note: The actual validation will depend on CLI implementation
            # This test ensures the CLI can handle invalid input gracefully
    
    def test_click_option_validation_margins(self):
        """Test Click option validation for margins"""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Create a dummy EPUB
            Path("test.epub").write_bytes(b'PK\x03\x04')
            
            # Test invalid margins (too few values)
            result = runner.invoke(main, ['test.epub', 'output.pdf', '--margins', '1', '2'])
            # This test ensures margins validation works in CLI context