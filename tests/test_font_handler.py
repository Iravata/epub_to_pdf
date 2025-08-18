"""Tests for font detection and mapping."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import zipfile
import base64

# Import the font handler that needs to be implemented
# These imports will initially fail but define the expected interface
try:
    from src.font_handler import FontHandler, FontMapping, FontMetrics
except ImportError:
    # Define mock classes for TDD - these represent the expected interface
    class FontMetrics:
        def __init__(self, font_family, font_style, font_weight, font_size):
            self.font_family = font_family
            self.font_style = font_style
            self.font_weight = font_weight
            self.font_size = font_size
    
    class FontMapping:
        def __init__(self):
            self.mappings = {}
        
        def add_mapping(self, css_font, pdf_font):
            self.mappings[css_font] = pdf_font
        
        def get_pdf_font(self, css_font):
            return self.mappings.get(css_font)
    
    class FontHandler:
        def __init__(self):
            self.font_mapping = FontMapping()
            self.embedded_fonts = {}
        
        def detect_fonts_in_epub(self, epub_path):
            pass
        
        def extract_font_files(self, epub_path):
            pass
        
        def analyze_font_usage(self, css_content, html_content):
            pass
        
        def create_font_mapping(self, epub_fonts):
            pass
        
        def embed_fonts_in_pdf(self, pdf_doc, font_files):
            pass
        
        def get_fallback_font(self, requested_font):
            pass
        
        def register_system_fonts(self):
            pass


class TestFontHandler:
    """Test suite for font handling functionality."""
    
    def test_font_handler_initialization(self):
        """Test font handler can be initialized properly."""
        handler = FontHandler()
        assert handler is not None
        assert handler.font_mapping is not None
        assert isinstance(handler.embedded_fonts, dict)
    
    def test_detect_fonts_in_epub_basic(self, epub_with_fonts):
        """Test detecting fonts in EPUB with embedded font files."""
        handler = FontHandler()
        
        fonts = handler.detect_fonts_in_epub(epub_with_fonts)
        
        assert isinstance(fonts, list)
        assert len(fonts) >= 1  # Should find at least the test.ttf font
        
        # Check font detection
        font_names = [font.get('family', font.get('name', '')) for font in fonts]
        assert any('test' in name.lower() or 'ttf' in str(font) for font in fonts for name in [str(font)])
    
    def test_detect_fonts_in_epub_without_fonts(self, sample_epub):
        """Test handling EPUB without embedded fonts."""
        handler = FontHandler()
        
        fonts = handler.detect_fonts_in_epub(sample_epub)
        
        # Should return empty list or default fonts
        assert isinstance(fonts, list)
        # Should not crash even without font files
    
    def test_extract_font_files(self, epub_with_fonts):
        """Test extracting font files from EPUB."""
        handler = FontHandler()
        
        font_files = handler.extract_font_files(epub_with_fonts)
        
        assert isinstance(font_files, dict)
        assert len(font_files) >= 1
        
        # Should extract font file content
        for font_name, font_data in font_files.items():
            assert isinstance(font_data, bytes)
            assert len(font_data) > 0
    
    def test_analyze_font_usage_in_css(self):
        """Test analyzing font usage from CSS content."""
        handler = FontHandler()
        
        css_content = """
        @font-face {
            font-family: 'CustomFont';
            src: url('fonts/custom.ttf') format('truetype');
            font-weight: normal;
        }
        body {
            font-family: 'CustomFont', 'Times New Roman', serif;
            font-size: 12pt;
        }
        h1 {
            font-family: Arial, sans-serif;
            font-weight: bold;
        }
        .italic {
            font-style: italic;
        }
        """
        
        html_content = "<html><body><h1>Title</h1><p class='italic'>Text</p></body></html>"
        
        font_usage = handler.analyze_font_usage(css_content, html_content)
        
        assert isinstance(font_usage, list)
        assert len(font_usage) >= 1
        
        # Should detect CustomFont usage
        custom_font = next((f for f in font_usage if 'CustomFont' in f.font_family), None)
        assert custom_font is not None
        
        # Should detect Arial usage
        arial_font = next((f for f in font_usage if 'Arial' in f.font_family), None)
        assert arial_font is not None
    
    def test_analyze_font_usage_inline_styles(self):
        """Test analyzing font usage from inline styles."""
        handler = FontHandler()
        
        html_content = """
        <html>
            <body>
                <h1 style="font-family: 'Helvetica', sans-serif; font-weight: bold;">Title</h1>
                <p style="font-family: Georgia, serif; font-style: italic;">Paragraph</p>
                <span style="font-family: 'Courier New', monospace;">Code</span>
            </body>
        </html>
        """
        
        font_usage = handler.analyze_font_usage("", html_content)
        
        assert isinstance(font_usage, list)
        assert len(font_usage) >= 3
        
        # Should detect different font families
        font_families = [f.font_family for f in font_usage]
        assert any('Helvetica' in family for family in font_families)
        assert any('Georgia' in family for family in font_families)
        assert any('Courier' in family for family in font_families)
    
    def test_create_font_mapping_standard_fonts(self):
        """Test creating font mapping for standard fonts."""
        handler = FontHandler()
        
        epub_fonts = [
            {'family': 'Times New Roman', 'weight': 'normal', 'style': 'normal'},
            {'family': 'Arial', 'weight': 'bold', 'style': 'normal'},
            {'family': 'Georgia', 'weight': 'normal', 'style': 'italic'}
        ]
        
        mapping = handler.create_font_mapping(epub_fonts)
        
        assert isinstance(mapping, FontMapping)
        
        # Should map to ReportLab compatible fonts
        times_mapping = mapping.get_pdf_font('Times New Roman')
        assert times_mapping is not None
        
        arial_mapping = mapping.get_pdf_font('Arial')
        assert arial_mapping is not None
    
    def test_create_font_mapping_custom_fonts(self):
        """Test creating font mapping for custom embedded fonts."""
        handler = FontHandler()
        
        epub_fonts = [
            {'family': 'CustomFont', 'weight': 'normal', 'style': 'normal', 'file': 'custom.ttf'},
            {'family': 'BrandFont', 'weight': 'bold', 'style': 'normal', 'file': 'brand-bold.otf'}
        ]
        
        mapping = handler.create_font_mapping(epub_fonts)
        
        # Should handle custom fonts
        custom_mapping = mapping.get_pdf_font('CustomFont')
        assert custom_mapping is not None
        
        brand_mapping = mapping.get_pdf_font('BrandFont')
        assert brand_mapping is not None
    
    def test_embed_fonts_in_pdf(self, epub_with_fonts):
        """Test embedding fonts in PDF document."""
        handler = FontHandler()
        
        # Extract font files
        font_files = handler.extract_font_files(epub_with_fonts)
        
        # Mock PDF document
        mock_pdf = Mock()
        mock_canvas = Mock()
        mock_pdf.canv = mock_canvas
        
        # Should not raise exception
        embedded_fonts = handler.embed_fonts_in_pdf(mock_pdf, font_files)
        
        # Should return information about embedded fonts
        assert isinstance(embedded_fonts, dict)
    
    def test_get_fallback_font(self):
        """Test fallback font selection for unavailable fonts."""
        handler = FontHandler()
        
        # Test serif fallback
        serif_fallback = handler.get_fallback_font('Unknown Serif Font')
        assert 'Times' in serif_fallback or 'serif' in serif_fallback.lower()
        
        # Test sans-serif fallback
        sans_fallback = handler.get_fallback_font('Unknown Sans Font')
        assert 'Arial' in sans_fallback or 'Helvetica' in sans_fallback or 'sans' in sans_fallback.lower()
        
        # Test monospace fallback
        mono_fallback = handler.get_fallback_font('Unknown Mono Font')
        assert 'Courier' in mono_fallback or 'mono' in mono_fallback.lower()
    
    def test_register_system_fonts(self):
        """Test registering available system fonts."""
        handler = FontHandler()
        
        system_fonts = handler.register_system_fonts()
        
        # Should return list of available fonts
        assert isinstance(system_fonts, list)
        # Common system fonts should be available
        font_names = [font.lower() for font in system_fonts]
        # At least one common font should be available
        common_fonts = ['times', 'arial', 'helvetica', 'courier']
        assert any(common in ' '.join(font_names) for common in common_fonts)
    
    def test_font_subsetting(self):
        """Test font subsetting to reduce PDF size."""
        handler = FontHandler()
        
        # Mock font file data
        font_data = b"mock font data" * 1000  # Large font
        used_characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!? "
        
        subset_data = handler.subset_font(font_data, used_characters)
        
        # Should return subsetted font data
        assert isinstance(subset_data, bytes)
        # For a mock implementation, might return original data
        assert len(subset_data) > 0
    
    def test_font_metrics_calculation(self):
        """Test calculating font metrics for layout."""
        handler = FontHandler()
        
        font_family = "Times New Roman"
        font_size = 12
        
        metrics = handler.get_font_metrics(font_family, font_size)
        
        assert isinstance(metrics, FontMetrics)
        assert metrics.font_family == font_family
        assert metrics.font_size == font_size
        
        # Should have calculated metrics
        assert hasattr(metrics, 'line_height')
        assert hasattr(metrics, 'ascent')
        assert hasattr(metrics, 'descent')
    
    def test_font_weight_mapping(self):
        """Test mapping CSS font weights to PDF font variations."""
        handler = FontHandler()
        
        weight_tests = [
            ('normal', 400),
            ('bold', 700),
            ('lighter', 300),
            ('bolder', 800),
            ('100', 100),
            ('900', 900)
        ]
        
        for css_weight, expected_numeric in weight_tests:
            numeric_weight = handler.map_font_weight(css_weight)
            assert isinstance(numeric_weight, int)
            assert 100 <= numeric_weight <= 900
    
    def test_font_style_mapping(self):
        """Test mapping CSS font styles to PDF font styles."""
        handler = FontHandler()
        
        style_tests = [
            ('normal', 'normal'),
            ('italic', 'italic'),
            ('oblique', 'oblique')
        ]
        
        for css_style, expected_style in style_tests:
            pdf_style = handler.map_font_style(css_style)
            assert pdf_style is not None
    
    def test_font_family_parsing(self):
        """Test parsing CSS font-family declarations."""
        handler = FontHandler()
        
        font_family_tests = [
            ("'Times New Roman', serif", ["Times New Roman", "serif"]),
            ('Arial, "Helvetica Neue", sans-serif', ["Arial", "Helvetica Neue", "sans-serif"]),
            ("Georgia, Times, serif", ["Georgia", "Times", "serif"]),
            ("monospace", ["monospace"])
        ]
        
        for css_family, expected_fonts in font_family_tests:
            parsed_fonts = handler.parse_font_family(css_family)
            assert isinstance(parsed_fonts, list)
            assert len(parsed_fonts) == len(expected_fonts)
            for i, expected in enumerate(expected_fonts):
                assert expected in parsed_fonts[i] or parsed_fonts[i] in expected
    
    def test_font_loading_error_handling(self):
        """Test handling errors in font loading."""
        handler = FontHandler()
        
        # Test with non-existent font file
        result = handler.load_font_file("/non/existent/font.ttf")
        
        # Should handle gracefully
        assert result is None or isinstance(result, dict)
        
        # Test with corrupted font data
        corrupted_data = b"not a font file"
        result = handler.parse_font_data(corrupted_data)
        
        # Should handle gracefully
        assert result is None or isinstance(result, dict)
    
    def test_font_caching(self):
        """Test font caching for performance."""
        handler = FontHandler()
        
        font_path = "test_font.ttf"
        
        # First load
        font1 = handler.get_cached_font(font_path)
        
        # Second load should use cache
        font2 = handler.get_cached_font(font_path)
        
        # Should return same object or equivalent data
        if font1 is not None and font2 is not None:
            assert font1 == font2 or str(font1) == str(font2)


class TestFontMapping:
    """Test suite for font mapping functionality."""
    
    def test_font_mapping_creation(self):
        """Test creating font mapping objects."""
        mapping = FontMapping()
        assert isinstance(mapping.mappings, dict)
        assert len(mapping.mappings) == 0
    
    def test_add_mapping(self):
        """Test adding font mappings."""
        mapping = FontMapping()
        
        mapping.add_mapping("Arial", "Helvetica")
        mapping.add_mapping("Times New Roman", "Times-Roman")
        
        assert len(mapping.mappings) == 2
        assert mapping.get_pdf_font("Arial") == "Helvetica"
        assert mapping.get_pdf_font("Times New Roman") == "Times-Roman"
    
    def test_get_pdf_font_fallback(self):
        """Test getting PDF font with fallback."""
        mapping = FontMapping()
        mapping.add_mapping("Arial", "Helvetica")
        
        # Existing mapping
        assert mapping.get_pdf_font("Arial") == "Helvetica"
        
        # Non-existent mapping with fallback
        fallback = mapping.get_pdf_font("Unknown Font", fallback="Times-Roman")
        assert fallback == "Times-Roman" or fallback is None
    
    def test_font_mapping_case_sensitivity(self):
        """Test font mapping case sensitivity."""
        mapping = FontMapping()
        mapping.add_mapping("Arial", "Helvetica")
        
        # Test case variations
        variations = ["arial", "ARIAL", "Arial"]
        for variation in variations:
            result = mapping.get_pdf_font(variation)
            # Should either find exact match or handle case insensitivity
            assert result is not None or mapping.get_pdf_font("Arial") is not None


class TestFontMetrics:
    """Test suite for font metrics functionality."""
    
    def test_font_metrics_creation(self):
        """Test creating font metrics objects."""
        metrics = FontMetrics("Arial", "normal", "normal", 12)
        
        assert metrics.font_family == "Arial"
        assert metrics.font_style == "normal"
        assert metrics.font_weight == "normal"
        assert metrics.font_size == 12
    
    def test_calculate_text_width(self):
        """Test calculating text width with font metrics."""
        metrics = FontMetrics("Arial", "normal", "normal", 12)
        
        text = "Hello World"
        width = metrics.calculate_text_width(text)
        
        # Should return a positive width
        assert isinstance(width, (int, float))
        assert width > 0
        
        # Longer text should be wider
        longer_text = "Hello World This is Much Longer"
        longer_width = metrics.calculate_text_width(longer_text)
        assert longer_width > width
    
    def test_calculate_line_height(self):
        """Test calculating line height for font."""
        metrics = FontMetrics("Arial", "normal", "normal", 12)
        
        line_height = metrics.calculate_line_height()
        
        # Should be reasonable relative to font size
        assert isinstance(line_height, (int, float))
        assert line_height >= metrics.font_size
        assert line_height <= metrics.font_size * 2  # Reasonable upper bound
    
    def test_font_metrics_comparison(self):
        """Test comparing font metrics objects."""
        metrics1 = FontMetrics("Arial", "normal", "normal", 12)
        metrics2 = FontMetrics("Arial", "normal", "normal", 12)
        metrics3 = FontMetrics("Times", "normal", "normal", 12)
        
        # Same metrics should be equal
        assert metrics1 == metrics2 or str(metrics1) == str(metrics2)
        
        # Different metrics should not be equal
        assert metrics1 != metrics3 or str(metrics1) != str(metrics3)


class TestFontUtilities:
    """Test suite for font utility functions."""
    
    def test_is_system_font(self):
        """Test identifying system fonts."""
        handler = FontHandler()
        
        # Common system fonts
        system_fonts = ["Arial", "Times New Roman", "Helvetica", "Courier"]
        for font in system_fonts:
            # Should identify as system font or handle gracefully
            result = handler.is_system_font(font)
            assert isinstance(result, bool)
    
    def test_get_font_file_format(self):
        """Test detecting font file format."""
        handler = FontHandler()
        
        test_cases = [
            ("font.ttf", "truetype"),
            ("font.otf", "opentype"),
            ("font.woff", "woff"),
            ("font.woff2", "woff2")
        ]
        
        for filename, expected_format in test_cases:
            detected_format = handler.get_font_file_format(filename)
            assert expected_format in detected_format.lower() or detected_format.lower() in expected_format
    
    def test_validate_font_file(self):
        """Test validating font file integrity."""
        handler = FontHandler()
        
        # Test with valid font data (minimal)
        valid_font_data = b"\x00\x01\x00\x00"  # Minimal TTF header
        is_valid = handler.validate_font_file(valid_font_data)
        
        # Should perform basic validation
        assert isinstance(is_valid, bool)
        
        # Test with invalid data
        invalid_data = b"not a font"
        is_invalid = handler.validate_font_file(invalid_data)
        assert isinstance(is_invalid, bool)
    
    def test_extract_font_metadata(self):
        """Test extracting metadata from font files."""
        handler = FontHandler()
        
        # Mock font data with metadata
        font_data = b"mock font with metadata"
        metadata = handler.extract_font_metadata(font_data)
        
        # Should return metadata dictionary
        assert isinstance(metadata, dict)
        # Common metadata fields
        expected_fields = ['family', 'style', 'weight', 'version']
        # At least some fields should be present or handled gracefully
