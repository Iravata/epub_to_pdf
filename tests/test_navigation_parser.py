import pytest
from src.navigation_parser import NavigationParser

class TestNavigationParser:
    def test_parse_toc_from_ncx(self, epub_with_ncx):
        """Test parsing table of contents from NCX file"""
        parser = NavigationParser(epub_with_ncx)
        toc = parser.parse_toc()
        
        assert len(toc) > 0
        assert 'title' in toc[0]
        assert 'href' in toc[0]
        assert 'level' in toc[0]
    
    def test_parse_toc_from_nav(self, epub3_with_nav):
        """Test parsing table of contents from EPUB3 nav document"""
        parser = NavigationParser(epub3_with_nav)
        toc = parser.parse_toc()
        
        assert len(toc) > 0
        assert toc[0]['level'] >= 0
    
    def test_generate_toc_from_headings(self, epub_without_toc):
        """Test TOC generation from HTML headings when no TOC exists"""
        parser = NavigationParser(epub_without_toc)
        toc = parser.parse_toc()
        
        assert len(toc) > 0
        assert 'generated' in toc[0]
        assert toc[0]['generated'] == True
    
    def test_toc_hierarchy_preserved(self, nested_toc_epub):
        """Test nested TOC structure is preserved"""
        parser = NavigationParser(nested_toc_epub)
        toc = parser.parse_toc()
        
        # Find item with children
        parent = next((item for item in toc if 'children' in item), None)
        assert parent is not None
        assert len(parent['children']) > 0