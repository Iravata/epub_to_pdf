import pytest
from src.metadata_parser import MetadataParser

class TestMetadataParser:
    def test_parse_basic_metadata(self, sample_epub):
        """Test parsing of basic metadata fields"""
        parser = MetadataParser(sample_epub)
        metadata = parser.parse()
        
        assert 'title' in metadata
        assert 'author' in metadata
        assert 'language' in metadata
        assert metadata['title'] is not None
    
    def test_parse_optional_metadata(self, sample_epub):
        """Test parsing of optional metadata fields"""
        parser = MetadataParser(sample_epub)
        metadata = parser.parse()
        
        # These may be None but should exist as keys
        assert 'publisher' in metadata
        assert 'publication_date' in metadata
        assert 'isbn' in metadata
        assert 'description' in metadata
    
    def test_handle_missing_metadata_gracefully(self, minimal_epub):
        """Test parser handles missing metadata without crashing"""
        parser = MetadataParser(minimal_epub)
        metadata = parser.parse()
        
        assert metadata['title'] == 'Untitled'
        assert metadata['author'] == 'Unknown Author'
    
    def test_parse_multiple_authors(self, multi_author_epub):
        """Test parsing EPUBs with multiple authors"""
        parser = MetadataParser(multi_author_epub)
        metadata = parser.parse()
        
        assert isinstance(metadata['author'], list)
        assert len(metadata['author']) > 1