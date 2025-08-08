import pytest
from src.html_converter import HTMLToPDFConverter

class TestHTMLConverter:
    def test_convert_simple_html(self):
        """Test conversion of simple HTML to PDF elements"""
        html = "<p>Hello World</p>"
        converter = HTMLToPDFConverter()
        elements = converter.convert(html)
        
        assert len(elements) > 0
        assert elements[0]['type'] == 'paragraph'
        assert elements[0]['text'] == 'Hello World'
    
    def test_convert_headings(self):
        """Test conversion of HTML headings"""
        html = "<h1>Title</h1><h2>Subtitle</h2>"
        converter = HTMLToPDFConverter()
        elements = converter.convert(html)
        
        assert len(elements) == 2
        assert elements[0]['type'] == 'heading'
        assert elements[0]['level'] == 1
        assert elements[1]['level'] == 2
    
    def test_convert_formatted_text(self):
        """Test conversion of bold, italic, etc."""
        html = "<p>Normal <b>bold</b> <i>italic</i> text</p>"
        converter = HTMLToPDFConverter()
        elements = converter.convert(html)
        
        assert len(elements) > 0
        assert 'styles' in elements[0]
    
    def test_convert_lists(self):
        """Test conversion of HTML lists"""
        html = "<ul><li>Item 1</li><li>Item 2</li></ul>"
        converter = HTMLToPDFConverter()
        elements = converter.convert(html)
        
        assert len(elements) > 0
        assert elements[0]['type'] == 'list'
        assert len(elements[0]['items']) == 2
    
    def test_handle_images(self):
        """Test handling of image tags"""
        html = '<img src="image.jpg" alt="Test">'
        converter = HTMLToPDFConverter()
        elements = converter.convert(html)
        
        assert len(elements) > 0
        assert elements[0]['type'] == 'image'
        assert elements[0]['src'] == 'image.jpg'