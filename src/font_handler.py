from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import List, Set, Dict, Any, Optional
import re
from pathlib import Path
import zipfile
import os
from bs4 import BeautifulSoup


class FontMetrics:
    """Represents font metrics for layout calculations."""
    
    def __init__(self, font_family: str, font_style: str, font_weight: str, font_size: float):
        self.font_family = font_family
        self.font_style = font_style
        self.font_weight = font_weight
        self.font_size = font_size
    
    def calculate_text_width(self, text: str) -> float:
        """Calculate the width of text in points."""
        # Rough estimation - in real implementation would use actual font metrics
        return len(text) * self.font_size * 0.6
    
    def calculate_line_height(self) -> float:
        """Calculate line height in points."""
        return self.font_size * 1.2
    
    def compare_metrics(self, other: 'FontMetrics') -> Dict[str, bool]:
        """Compare font metrics with another FontMetrics instance."""
        return {
            'same_family': self.font_family == other.font_family,
            'same_style': self.font_style == other.font_style,
            'same_weight': self.font_weight == other.font_weight,
            'same_size': abs(self.font_size - other.font_size) < 0.1
        }


class FontMapping:
    """Manages font mapping from CSS fonts to PDF fonts."""
    
    def __init__(self):
        self.mappings = {}
        self.fallback_fonts = {
            'serif': 'Times-Roman',
            'sans-serif': 'Helvetica',
            'monospace': 'Courier'
        }
    
    def add_mapping(self, css_font: str, pdf_font: str):
        """Add a mapping from CSS font to PDF font."""
        self.mappings[css_font] = pdf_font
    
    def get_pdf_font(self, css_font: str) -> str:
        """Get the PDF font name for a CSS font."""
        return self.mappings.get(css_font, self.get_fallback_font(css_font))
    
    def get_fallback_font(self, css_font: str) -> str:
        """Get a fallback font for an unmapped CSS font."""
        css_font_lower = css_font.lower()
        
        # Check for font family categories
        for category, pdf_font in self.fallback_fonts.items():
            if category in css_font_lower:
                return pdf_font
        
        # Default fallback
        return 'Times-Roman'


class FontUtilities:
    """Utility functions for font handling."""
    
    @staticmethod
    def is_system_font(font_name: str) -> bool:
        """Check if a font is a system font."""
        system_fonts = {
            'Times-Roman', 'Times-Bold', 'Times-Italic', 'Times-BoldItalic',
            'Helvetica', 'Helvetica-Bold', 'Helvetica-Oblique', 'Helvetica-BoldOblique',
            'Courier', 'Courier-Bold', 'Courier-Oblique', 'Courier-BoldOblique'
        }
        return font_name in system_fonts
    
    @staticmethod
    def get_font_file_format(font_path: str) -> Optional[str]:
        """Get the format of a font file."""
        ext = Path(font_path).suffix.lower()
        format_map = {
            '.ttf': 'truetype',
            '.otf': 'opentype',
            '.woff': 'woff',
            '.woff2': 'woff2'
        }
        return format_map.get(ext)
    
    @staticmethod
    def validate_font_file(font_path: str) -> bool:
        """Validate if a file is a valid font file."""
        if not os.path.exists(font_path):
            return False
        
        valid_extensions = {'.ttf', '.otf', '.woff', '.woff2'}
        return Path(font_path).suffix.lower() in valid_extensions
    
    @staticmethod
    def extract_font_metadata(font_path: str) -> Dict[str, Any]:
        """Extract metadata from a font file (simplified)."""
        if not FontUtilities.validate_font_file(font_path):
            return {}
        
        # This would typically use a font parsing library
        # For now, return basic info based on filename
        font_name = Path(font_path).stem
        return {
            'name': font_name,
            'format': FontUtilities.get_font_file_format(font_path),
            'path': font_path
        }


class FontHandler:
    """Handle font detection and mapping for PDF"""
    
    # Font mapping from web to PDF
    FONT_MAP = {
        # Sans-serif fonts
        'Arial': 'Helvetica',
        'Helvetica': 'Helvetica',
        'Verdana': 'Helvetica',
        'Tahoma': 'Helvetica',
        'Trebuchet MS': 'Helvetica',
        'sans-serif': 'Helvetica',
        
        # Serif fonts
        'Times New Roman': 'Times-Roman',
        'Times': 'Times-Roman',
        'Georgia': 'Times-Roman',
        'Garamond': 'Times-Roman',
        'serif': 'Times-Roman',
        
        # Monospace fonts
        'Courier New': 'Courier',
        'Courier': 'Courier',
        'Consolas': 'Courier',
        'Monaco': 'Courier',
        'monospace': 'Courier',
    }
    
    def __init__(self):
        self.registered_fonts = set()
        self.font_mapping = FontMapping()
        self.embedded_fonts = {}
        self.font_cache = {}
    
    def detect_fonts(self, css: str) -> Set[str]:
        """Detect font families used in CSS"""
        fonts = set()
        
        # Find font-family declarations
        pattern = r'font-family:\s*([^;]+)'
        matches = re.findall(pattern, css, re.IGNORECASE)
        
        for match in matches:
            # Parse font list
            font_list = match.split(',')
            for font in font_list:
                # Clean up font name
                font = font.strip().strip('"\'')
                fonts.add(font)
        
        return fonts
    
    def map_font(self, font_name: str) -> str:
        """Map web font to PDF font"""
        # Check registered custom fonts first
        if font_name in self.registered_fonts:
            return font_name
        
        # Use mapping table
        return self.FONT_MAP.get(font_name, 'Helvetica')
    
    def register_font(self, font_name: str, font_path: str) -> bool:
        """Register custom TTF font"""
        try:
            # KISS: Only support TTF fonts
            if not font_path.endswith('.ttf'):
                return False
            
            # Register with ReportLab
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            self.registered_fonts.add(font_name)
            return True
            
        except Exception:
            return False
    
    def is_font_available(self, font_name: str) -> bool:
        """Check if font is available for PDF"""
        if font_name in self.registered_fonts:
            return True
        
        return font_name in self.FONT_MAP
    
    def get_font_style(self, css_style: Dict[str, str]) -> str:
        """Get PDF font name from CSS style"""
        # Extract font properties
        family = css_style.get('font-family', 'sans-serif')
        weight = css_style.get('font-weight', 'normal')
        style = css_style.get('font-style', 'normal')
        
        # Parse font family (take first available)
        fonts = family.split(',')
        base_font = 'Helvetica'
        
        for font in fonts:
            font = font.strip().strip('"\'')
            mapped = self.map_font(font)
            if mapped:
                base_font = mapped
                break
        
        # Apply weight and style
        if 'Times' in base_font:
            if weight == 'bold' and style == 'italic':
                return 'Times-BoldItalic'
            elif weight == 'bold':
                return 'Times-Bold'
            elif style == 'italic':
                return 'Times-Italic'
            else:
                return 'Times-Roman'
        elif 'Courier' in base_font:
            if weight == 'bold' and style == 'oblique':
                return 'Courier-BoldOblique'
            elif weight == 'bold':
                return 'Courier-Bold'
            elif style == 'oblique':
                return 'Courier-Oblique'
            else:
                return 'Courier'
        else:  # Helvetica family
            if weight == 'bold' and style == 'italic':
                return 'Helvetica-BoldOblique'
            elif weight == 'bold':
                return 'Helvetica-Bold'
            elif style == 'italic':
                return 'Helvetica-Oblique'
            else:
                return 'Helvetica'
    
    def detect_fonts_in_epub(self, epub_path: str) -> List[Dict[str, Any]]:
        """Detect fonts embedded in EPUB file."""
        fonts = []
        
        try:
            with zipfile.ZipFile(epub_path, 'r') as zip_file:
                # Find font files
                font_files = [f for f in zip_file.namelist() 
                             if any(f.endswith(ext) for ext in ['.ttf', '.otf', '.woff', '.woff2'])]
                
                for font_file in font_files:
                    font_info = {
                        'path': font_file,
                        'name': Path(font_file).stem,
                        'family': Path(font_file).stem.replace('-', ' '),
                        'format': FontUtilities.get_font_file_format(font_file)
                    }
                    fonts.append(font_info)
        except:
            pass  # Return empty list if EPUB can't be processed
        
        return fonts
    
    def extract_font_files(self, epub_path: str) -> Dict[str, bytes]:
        """Extract font files from EPUB as bytes."""
        font_files = {}
        
        try:
            with zipfile.ZipFile(epub_path, 'r') as zip_file:
                # Find and extract font files
                for file_path in zip_file.namelist():
                    if any(file_path.endswith(ext) for ext in ['.ttf', '.otf', '.woff', '.woff2']):
                        try:
                            font_data = zip_file.read(file_path)
                            font_name = Path(file_path).stem
                            font_files[font_name] = font_data
                        except:
                            continue  # Skip files that can't be read
        except:
            pass
        
        return font_files
    
    def analyze_font_usage_in_css(self, css_content: str) -> Dict[str, List[str]]:
        """Analyze font usage in CSS content."""
        usage = {}
        
        # Extract font-family declarations
        pattern = r'([^{}]+)\s*\{\s*[^{}]*font-family:\s*([^;}]+)'
        matches = re.findall(pattern, css_content, re.IGNORECASE)
        
        for selector, font_family in matches:
            selector = selector.strip()
            fonts = [f.strip().strip('\'"') for f in font_family.split(',')]
            usage[selector] = fonts
        
        return usage
    
    def analyze_font_usage_inline_styles(self, html_content: str) -> Dict[str, List[str]]:
        """Analyze font usage in inline styles."""
        usage = {}
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find elements with inline font-family styles
        styled_elements = soup.find_all(attrs={'style': True})
        
        for i, element in enumerate(styled_elements):
            style = element.get('style', '')
            if 'font-family' in style:
                # Extract font-family value
                pattern = r'font-family:\s*([^;]+)'
                match = re.search(pattern, style, re.IGNORECASE)
                if match:
                    fonts = [f.strip().strip('\'"') for f in match.group(1).split(',')]
                    element_id = element.get('id', f"{element.name}_{i}")
                    usage[element_id] = fonts
        
        return usage
    
    def analyze_font_usage(self, css_content: str, html_content: str) -> List[Any]:
        """Analyze font usage in both CSS and HTML content."""
        css_usage = self.analyze_font_usage_in_css(css_content)
        html_usage = self.analyze_font_usage_inline_styles(html_content)
        
        # Combine and convert to font objects
        font_usage = []
        
        # Process CSS usage
        for selector, fonts in css_usage.items():
            for font in fonts:
                font_obj = type('FontUsage', (), {
                    'font_family': font,
                    'selector': selector,
                    'source': 'css'
                })()
                font_usage.append(font_obj)
        
        # Process HTML usage
        for element_id, fonts in html_usage.items():
            for font in fonts:
                font_obj = type('FontUsage', (), {
                    'font_family': font,
                    'selector': element_id,
                    'source': 'html'
                })()
                font_usage.append(font_obj)
        
        return font_usage
    
    def create_font_mapping_standard_fonts(self) -> FontMapping:
        """Create font mapping for standard fonts."""
        mapping = FontMapping()
        
        for css_font, pdf_font in self.FONT_MAP.items():
            mapping.add_mapping(css_font, pdf_font)
        
        return mapping
    
    def create_font_mapping_custom_fonts(self, epub_fonts: List[Dict[str, Any]]) -> FontMapping:
        """Create font mapping including custom fonts from EPUB."""
        mapping = self.create_font_mapping_standard_fonts()
        
        # Add custom fonts from EPUB
        for font_info in epub_fonts:
            font_family = font_info.get('family', font_info.get('name', ''))
            if font_family:
                # Use the custom font name directly
                mapping.add_mapping(font_family, font_family)
        
        return mapping
    
    def create_font_mapping(self, epub_fonts: List[Dict[str, Any]]) -> FontMapping:
        """Create complete font mapping."""
        return self.create_font_mapping_custom_fonts(epub_fonts)
    
    def embed_fonts_in_pdf(self, pdf_doc: Any, font_files: Dict[str, bytes]) -> bool:
        """Embed fonts in PDF document."""
        try:
            for font_name, font_data in font_files.items():
                # This would typically write font data to a temporary file
                # and register it with ReportLab
                # For now, just track that we attempted embedding
                self.embedded_fonts[font_name] = True
            return True
        except:
            return False
    
    def get_fallback_font(self, requested_font: str) -> str:
        """Get a fallback font for a requested font."""
        return self.font_mapping.get_fallback_font(requested_font)
    
    def register_system_fonts(self) -> int:
        """Register system fonts with ReportLab."""
        registered_count = 0
        
        # Standard ReportLab fonts are already registered
        system_fonts = [
            'Times-Roman', 'Times-Bold', 'Times-Italic', 'Times-BoldItalic',
            'Helvetica', 'Helvetica-Bold', 'Helvetica-Oblique', 'Helvetica-BoldOblique',
            'Courier', 'Courier-Bold', 'Courier-Oblique', 'Courier-BoldOblique'
        ]
        
        for font in system_fonts:
            self.registered_fonts.add(font)
            registered_count += 1
        
        return registered_count
    
    def font_subsetting(self, font_data: bytes, used_chars: Set[str]) -> bytes:
        """Create a subset of a font containing only used characters."""
        # This would require a font manipulation library like fonttools
        # For now, return the original font data
        return font_data
    
    def font_metrics_calculation(self, font_name: str, font_size: float) -> FontMetrics:
        """Calculate metrics for a font."""
        # Extract style and weight from font name
        font_style = 'italic' if 'italic' in font_name.lower() or 'oblique' in font_name.lower() else 'normal'
        font_weight = 'bold' if 'bold' in font_name.lower() else 'normal'
        
        # Get base family
        if font_name.startswith('Times'):
            family = 'Times'
        elif font_name.startswith('Helvetica'):
            family = 'Helvetica'
        elif font_name.startswith('Courier'):
            family = 'Courier'
        else:
            family = font_name
        
        return FontMetrics(family, font_style, font_weight, font_size)
    
    def font_weight_mapping(self, css_weight: str) -> str:
        """Map CSS font weight to PDF font weight."""
        weight_map = {
            'normal': 'normal',
            '400': 'normal',
            'bold': 'bold',
            '700': 'bold',
            'bolder': 'bold',
            'lighter': 'normal'
        }
        return weight_map.get(css_weight.lower(), 'normal')
    
    def font_style_mapping(self, css_style: str) -> str:
        """Map CSS font style to PDF font style."""
        style_map = {
            'normal': 'normal',
            'italic': 'italic',
            'oblique': 'oblique'
        }
        return style_map.get(css_style.lower(), 'normal')
    
    def font_family_parsing(self, font_family_string: str) -> List[str]:
        """Parse CSS font-family string into individual font names."""
        fonts = []
        
        for font in font_family_string.split(','):
            font = font.strip().strip('\'"')
            if font:
                fonts.append(font)
        
        return fonts
    
    def font_loading_error_handling(self, font_path: str) -> Optional[str]:
        """Handle font loading errors gracefully."""
        try:
            if not os.path.exists(font_path):
                return f"Font file not found: {font_path}"
            
            if not FontUtilities.validate_font_file(font_path):
                return f"Invalid font file format: {font_path}"
            
            # Attempt to register font
            font_name = Path(font_path).stem
            if self.register_font(font_name, font_path):
                return None  # Success
            else:
                return f"Failed to register font: {font_path}"
        
        except Exception as e:
            return f"Error loading font {font_path}: {str(e)}"
    
    def font_caching(self, font_name: str, font_data: Any) -> bool:
        """Cache font data for reuse."""
        try:
            self.font_cache[font_name] = font_data
            return True
        except:
            return False
