import pytest
from pathlib import Path
from src.resource_handler import ResourceHandler

class TestResourceHandler:
    def test_extract_images(self, epub_with_images):
        """Test extraction of images from EPUB"""
        handler = ResourceHandler(epub_with_images)
        images = handler.get_images()
        
        assert len(images) > 0
        assert 'name' in images[0]
        assert 'data' in images[0]
        assert 'mimetype' in images[0]
    
    def test_handle_different_image_formats(self, epub_with_images):
        """Test handling of various image formats"""
        handler = ResourceHandler(epub_with_images)
        images = handler.get_images()
        
        formats = {img['mimetype'] for img in images}
        # Should handle at least JPG and PNG
        assert any('jpeg' in fmt or 'jpg' in fmt for fmt in formats)
        assert any('png' in fmt for fmt in formats)
    
    def test_extract_css_files(self, epub_with_styles):
        """Test extraction of CSS stylesheets"""
        handler = ResourceHandler(epub_with_styles)
        styles = handler.get_stylesheets()
        
        assert len(styles) > 0
        assert 'name' in styles[0]
        assert 'content' in styles[0]
    
    def test_skip_unnecessary_resources(self, epub_with_fonts):
        """Test that fonts are skipped per YAGNI principle"""
        handler = ResourceHandler(epub_with_fonts)
        fonts = handler.get_fonts()
        
        # Phase 2 doesn't handle fonts yet
        assert fonts == []