import pytest
from src.style_mapper import StyleMapper

class TestStyleMapper:
    def test_map_font_size(self):
        """Test CSS font-size to PDF point size mapping"""
        mapper = StyleMapper()
        
        assert mapper.get_font_size('12px') == 12
        assert mapper.get_font_size('1em') == 12
        assert mapper.get_font_size('large') == 14
    
    def test_map_font_weight(self):
        """Test CSS font-weight to PDF font mapping"""
        mapper = StyleMapper()
        
        assert mapper.get_font_name('normal') == 'Helvetica'
        assert mapper.get_font_name('bold') == 'Helvetica-Bold'
        assert mapper.get_font_name('italic') == 'Helvetica-Oblique'
    
    def test_map_text_align(self):
        """Test CSS text-align to PDF alignment"""
        mapper = StyleMapper()
        
        assert mapper.get_alignment('left') == 0
        assert mapper.get_alignment('center') == 1
        assert mapper.get_alignment('right') == 2
    
    def test_map_colors(self):
        """Test CSS color to PDF color mapping"""
        mapper = StyleMapper()
        
        assert mapper.get_color('#000000') == (0, 0, 0)
        assert mapper.get_color('black') == (0, 0, 0)
        assert mapper.get_color('#FF0000') == (1, 0, 0)