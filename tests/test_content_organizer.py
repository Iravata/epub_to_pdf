import pytest
from src.content_organizer import ContentOrganizer

class TestContentOrganizer:
    def test_organize_chapters_in_order(self, sample_epub):
        """Test chapters are organized in reading order"""
        organizer = ContentOrganizer(sample_epub)
        chapters = organizer.get_chapters()
        
        assert len(chapters) > 0
        # Check that order is sequential starting from 0
        for i, chapter in enumerate(chapters):
            assert chapter['order'] == i
        
    def test_extract_chapter_content(self, sample_epub):
        """Test extraction of chapter HTML content"""
        organizer = ContentOrganizer(sample_epub)
        chapters = organizer.get_chapters()
        
        first_chapter = chapters[0]
        assert 'content' in first_chapter
        assert 'title' in first_chapter
        assert first_chapter['content'] is not None
    
    def test_identify_chapter_types(self, sample_epub):
        """Test identification of chapter vs. front/back matter"""
        organizer = ContentOrganizer(sample_epub)
        chapters = organizer.get_chapters()
        
        for chapter in chapters:
            assert 'type' in chapter
            assert chapter['type'] in ['cover', 'toc', 'chapter', 'appendix']
    
    def test_preserve_chapter_hierarchy(self, nested_epub):
        """Test preservation of nested chapter structure"""
        organizer = ContentOrganizer(nested_epub)
        structure = organizer.get_structure()
        
        assert 'children' in structure
        assert isinstance(structure['children'], list)