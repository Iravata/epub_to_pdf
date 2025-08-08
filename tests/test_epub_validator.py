import pytest
from pathlib import Path
from src.epub_validator import EPUBValidator

class TestEPUBValidator:
    def test_validates_epub_file_exists(self):
        """Test that validator checks if file exists"""
        validator = EPUBValidator("nonexistent.epub")
        assert validator.is_valid() == False
        assert "File not found" in validator.get_error()
    
    def test_validates_epub_extension(self, tmp_path):
        """Test that validator checks file extension"""
        # Create a non-EPUB file
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("Not an EPUB")
        
        validator = EPUBValidator(str(pdf_file))
        assert validator.is_valid() == False
        assert "Not an EPUB file" in validator.get_error()
    
    def test_validates_valid_epub(self, tmp_path):
        """Test that validator accepts valid EPUB"""
        # Create minimal valid EPUB structure
        epub_file = tmp_path / "test.epub"
        epub_file.write_bytes(b"PK")  # ZIP signature
        
        validator = EPUBValidator(str(epub_file))
        assert validator.is_valid() == True
        assert validator.get_error() is None