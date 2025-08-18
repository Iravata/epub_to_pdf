"""Tests for CSS style processing and preservation."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

# Import the CSS processor that needs to be implemented
# These imports will initially fail but define the expected interface
try:
    from src.css_processor import CSSProcessor, CSSStyle, CSSRule
except ImportError:
    # Define mock classes for TDD - these represent the expected interface
    class CSSStyle:
        def __init__(self, selector, properties):
            self.selector = selector
            self.properties = properties
    
    class CSSRule:
        def __init__(self, selector, declarations):
            self.selector = selector
            self.declarations = declarations
    
    class CSSProcessor:
        def __init__(self):
            pass
        
        def parse_css(self, css_content):
            pass
        
        def extract_styles_from_epub(self, epub_path):
            pass
        
        def merge_styles(self, style_list):
            pass
        
        def convert_to_pdf_styles(self, css_styles):
            pass
        
        def preserve_layout_styles(self, styles):
            pass


class TestCSSProcessor:
    """Test suite for CSS processing functionality."""
    
    def test_css_processor_initialization(self):
        """Test CSS processor can be initialized properly."""
        processor = CSSProcessor()
        assert processor is not None
        # Initially this will fail, defining expected behavior
    
    def test_parse_basic_css(self):
        """Test parsing basic CSS rules."""
        processor = CSSProcessor()
        css_content = """
        body {
            font-family: 'Times New Roman', serif;
            font-size: 12pt;
            margin: 1in;
        }
        h1 {
            font-size: 18pt;
            font-weight: bold;
            color: #333;
        }
        """
        
        styles = processor.parse_css(css_content)
        
        # Should return a list of CSS rules
        assert isinstance(styles, list)
        assert len(styles) == 2
        
        # Check body style
        body_style = next((s for s in styles if s.selector == 'body'), None)
        assert body_style is not None
        assert 'font-family' in body_style.properties
        assert body_style.properties['font-size'] == '12pt'
        
        # Check h1 style
        h1_style = next((s for s in styles if s.selector == 'h1'), None)
        assert h1_style is not None
        assert h1_style.properties['font-weight'] == 'bold'
    
    def test_parse_complex_css_selectors(self):
        """Test parsing complex CSS selectors and nested rules."""
        processor = CSSProcessor()
        css_content = """
        .chapter-title {
            font-size: 16pt;
            margin-bottom: 20px;
        }
        p.first-paragraph {
            text-indent: 0;
        }
        div > p {
            line-height: 1.5;
        }
        @media print {
            body { margin: 0.5in; }
        }
        """
        
        styles = processor.parse_css(css_content)
        
        # Should handle class selectors
        chapter_style = next((s for s in styles if s.selector == '.chapter-title'), None)
        assert chapter_style is not None
        
        # Should handle compound selectors
        first_para_style = next((s for s in styles if s.selector == 'p.first-paragraph'), None)
        assert first_para_style is not None
        
        # Should handle child selectors
        child_style = next((s for s in styles if s.selector == 'div > p'), None)
        assert child_style is not None
        
        # Should handle media queries (or at least not crash)
        assert len(styles) >= 3
    
    def test_extract_styles_from_epub(self, epub_with_styles):
        """Test extracting CSS styles from EPUB file."""
        processor = CSSProcessor()
        
        styles = processor.extract_styles_from_epub(epub_with_styles)
        
        # Should return extracted styles
        assert isinstance(styles, list)
        # Should find at least one style from the EPUB
        assert len(styles) > 0
        
        # Check that main.css content was extracted
        body_style = next((s for s in styles if s.selector == 'body'), None)
        if body_style:
            assert 'font-family' in body_style.properties
    
    def test_extract_styles_from_epub_without_css(self, sample_epub):
        """Test handling EPUB files without CSS stylesheets."""
        processor = CSSProcessor()
        
        styles = processor.extract_styles_from_epub(sample_epub)
        
        # Should return empty list or default styles
        assert isinstance(styles, list)
        # Should not crash even without CSS files
    
    def test_extract_inline_styles(self):
        """Test extracting inline styles from HTML content."""
        processor = CSSProcessor()
        html_content = """
        <html>
            <body>
                <h1 style="color: red; font-size: 24px;">Title</h1>
                <p style="margin: 10px; font-weight: bold;">Paragraph</p>
            </body>
        </html>
        """
        
        styles = processor.extract_inline_styles(html_content)
        
        assert isinstance(styles, list)
        assert len(styles) >= 2
        
        # Should extract h1 inline styles
        h1_inline = next((s for s in styles if 'color: red' in str(s)), None)
        assert h1_inline is not None
    
    def test_merge_conflicting_styles(self):
        """Test merging CSS styles with conflicts."""
        processor = CSSProcessor()
        
        styles = [
            CSSStyle('p', {'font-size': '12pt', 'color': 'black'}),
            CSSStyle('p', {'font-size': '14pt', 'margin': '10px'}),  # Conflicts with first
            CSSStyle('.highlight', {'color': 'red', 'font-weight': 'bold'})
        ]
        
        merged = processor.merge_styles(styles)
        
        # Should handle conflicts by precedence (later styles win)
        p_style = next((s for s in merged if s.selector == 'p'), None)
        assert p_style is not None
        assert p_style.properties['font-size'] == '14pt'  # Later value wins
        assert p_style.properties['color'] == 'black'     # Non-conflicting preserved
        assert p_style.properties['margin'] == '10px'     # New property added
    
    def test_convert_to_pdf_styles(self):
        """Test converting CSS styles to PDF-compatible format."""
        processor = CSSProcessor()
        
        css_styles = [
            CSSStyle('body', {
                'font-family': 'Times New Roman, serif',
                'font-size': '12pt',
                'margin': '1in',
                'line-height': '1.5'
            }),
            CSSStyle('h1', {
                'font-size': '18pt',
                'font-weight': 'bold',
                'color': '#333333',
                'margin-bottom': '20px'
            })
        ]
        
        pdf_styles = processor.convert_to_pdf_styles(css_styles)
        
        # Should convert to ReportLab-compatible styles
        assert isinstance(pdf_styles, dict)
        assert 'body' in pdf_styles
        assert 'h1' in pdf_styles
        
        # Check font conversion
        body_style = pdf_styles['body']
        assert 'fontName' in body_style
        assert body_style['fontSize'] == 12  # Convert pt to number
        
        # Check color conversion
        h1_style = pdf_styles['h1']
        assert 'textColor' in h1_style
    
    def test_preserve_layout_styles(self):
        """Test preserving important layout styles for PDF."""
        processor = CSSProcessor()
        
        styles = [
            CSSStyle('div', {
                'page-break-before': 'always',
                'page-break-after': 'avoid',
                'widows': '2',
                'orphans': '2'
            }),
            CSSStyle('table', {
                'page-break-inside': 'avoid',
                'border-collapse': 'collapse'
            })
        ]
        
        preserved = processor.preserve_layout_styles(styles)
        
        # Should preserve page-break properties
        div_style = next((s for s in preserved if s.selector == 'div'), None)
        assert div_style is not None
        assert 'page-break-before' in div_style.properties
        
        # Should preserve table layout properties
        table_style = next((s for s in preserved if s.selector == 'table'), None)
        assert table_style is not None
        assert 'page-break-inside' in table_style.properties
    
    def test_handle_font_face_rules(self):
        """Test handling @font-face CSS rules."""
        processor = CSSProcessor()
        css_content = """
        @font-face {
            font-family: 'CustomFont';
            src: url('fonts/custom.ttf') format('truetype');
            font-weight: normal;
            font-style: normal;
        }
        body {
            font-family: 'CustomFont', serif;
        }
        """
        
        styles = processor.parse_css(css_content)
        font_faces = processor.extract_font_faces(css_content)
        
        # Should extract font-face information
        assert isinstance(font_faces, list)
        assert len(font_faces) >= 1
        
        custom_font = font_faces[0]
        assert custom_font['family'] == 'CustomFont'
        assert 'custom.ttf' in custom_font['src']
    
    def test_css_specificity_calculation(self):
        """Test CSS specificity calculation for proper style precedence."""
        processor = CSSProcessor()
        
        # Test different selector specificity
        selectors = [
            'p',                    # specificity: 1
            '.class',              # specificity: 10
            '#id',                 # specificity: 100
            'div p',               # specificity: 2
            'div.class p',         # specificity: 12
            '#id div.class p'      # specificity: 112
        ]
        
        for selector in selectors:
            specificity = processor.calculate_specificity(selector)
            assert isinstance(specificity, int)
            assert specificity >= 0
        
        # Test precedence ordering
        assert processor.calculate_specificity('#id') > processor.calculate_specificity('.class')
        assert processor.calculate_specificity('.class') > processor.calculate_specificity('p')
    
    def test_css_validation(self):
        """Test CSS validation and error handling."""
        processor = CSSProcessor()
        
        # Valid CSS should parse without errors
        valid_css = "body { font-size: 12pt; }"
        styles = processor.parse_css(valid_css)
        assert len(styles) > 0
        
        # Invalid CSS should be handled gracefully
        invalid_css = "body { font-size: ; color }"
        styles = processor.parse_css(invalid_css)
        # Should not crash, might return empty list or partial results
        assert isinstance(styles, list)
    
    def test_css_minification_support(self):
        """Test parsing minified CSS content."""
        processor = CSSProcessor()
        
        minified_css = "body{font-size:12pt;margin:0}h1{color:#333;font-weight:bold}"
        styles = processor.parse_css(minified_css)
        
        assert len(styles) == 2
        body_style = next((s for s in styles if s.selector == 'body'), None)
        assert body_style is not None
        assert body_style.properties['font-size'] == '12pt'
    
    def test_css_import_handling(self):
        """Test handling CSS @import rules."""
        processor = CSSProcessor()
        
        css_with_imports = """
        @import url('base.css');
        @import 'print.css' print;
        
        body {
            font-family: serif;
        }
        """
        
        imports = processor.extract_imports(css_with_imports)
        styles = processor.parse_css(css_with_imports)
        
        # Should extract import information
        assert isinstance(imports, list)
        assert len(imports) >= 2
        
        # Should still parse other rules
        assert len(styles) >= 1
    
    def test_responsive_design_handling(self):
        """Test handling responsive design CSS for PDF adaptation."""
        processor = CSSProcessor()
        
        responsive_css = """
        body { font-size: 12pt; }
        
        @media screen {
            body { font-size: 14px; }
        }
        
        @media print {
            body { font-size: 10pt; margin: 0.5in; }
        }
        
        @media (max-width: 600px) {
            body { font-size: 16px; }
        }
        """
        
        print_styles = processor.extract_print_styles(responsive_css)
        
        # Should prioritize print styles for PDF
        assert isinstance(print_styles, list)
        print_body = next((s for s in print_styles if s.selector == 'body'), None)
        if print_body:
            assert print_body.properties['font-size'] == '10pt'
            assert 'margin' in print_body.properties


class TestCSSStyle:
    """Test suite for CSS Style representation."""
    
    def test_css_style_creation(self):
        """Test creating CSS style objects."""
        style = CSSStyle('p', {'font-size': '12pt', 'color': 'black'})
        
        assert style.selector == 'p'
        assert style.properties['font-size'] == '12pt'
        assert style.properties['color'] == 'black'
    
    def test_css_style_merge(self):
        """Test merging CSS style properties."""
        style1 = CSSStyle('p', {'font-size': '12pt', 'color': 'black'})
        style2 = CSSStyle('p', {'font-size': '14pt', 'margin': '10px'})
        
        merged = style1.merge(style2)
        
        # Later properties should override
        assert merged.properties['font-size'] == '14pt'
        # Non-conflicting properties should be preserved
        assert merged.properties['color'] == 'black'
        assert merged.properties['margin'] == '10px'
    
    def test_css_style_to_reportlab(self):
        """Test converting CSS style to ReportLab format."""
        style = CSSStyle('p', {
            'font-size': '12pt',
            'color': '#333333',
            'font-weight': 'bold',
            'text-align': 'center'
        })
        
        rl_style = style.to_reportlab()
        
        # Should convert to ReportLab compatible format
        assert 'fontSize' in rl_style
        assert rl_style['fontSize'] == 12
        assert 'textColor' in rl_style
        assert 'fontName' in rl_style or 'bold' in str(rl_style['fontName']).lower()
        assert 'alignment' in rl_style


class TestCSSRule:
    """Test suite for CSS Rule representation."""
    
    def test_css_rule_creation(self):
        """Test creating CSS rule objects."""
        declarations = {'font-size': '12pt', 'color': 'black'}
        rule = CSSRule('p', declarations)
        
        assert rule.selector == 'p'
        assert rule.declarations == declarations
    
    def test_css_rule_specificity(self):
        """Test CSS rule specificity calculation."""
        rule = CSSRule('div.class p#id', {})
        specificity = rule.calculate_specificity()
        
        # Should calculate proper specificity
        assert isinstance(specificity, int)
        assert specificity > 0
    
    def test_css_rule_validation(self):
        """Test CSS rule validation."""
        valid_rule = CSSRule('p', {'font-size': '12pt'})
        invalid_rule = CSSRule('', {})  # Empty selector
        
        assert valid_rule.is_valid()
        assert not invalid_rule.is_valid()
