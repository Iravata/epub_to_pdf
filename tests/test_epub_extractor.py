import pytest
from pathlib import Path
from src.epub_extractor import EPUBExtractor

class TestEPUBExtractor:
    def test_extract_raises_on_invalid_file(self):
        """Test extractor raises exception for invalid file"""
        extractor = EPUBExtractor("invalid.epub")
        with pytest.raises(FileNotFoundError):
            extractor.extract()
    
    def test_extract_returns_basic_structure(self, sample_epub):
        """Test extractor returns basic EPUB structure"""
        extractor = EPUBExtractor(sample_epub)
        result = extractor.extract()
        
        assert 'metadata' in result
        assert 'content_files' in result
        assert isinstance(result['content_files'], list)