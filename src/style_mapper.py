from typing import Tuple, Optional

class StyleMapper:
    """Map CSS styles to PDF styles (KISS principle)"""
    
    # Font size mapping (CSS -> points)
    FONT_SIZE_MAP = {
        'xx-small': 8,
        'x-small': 9,
        'small': 10,
        'medium': 12,
        'large': 14,
        'x-large': 16,
        'xx-large': 18
    }
    
    # Font family mapping
    FONT_MAP = {
        'normal': 'Helvetica',
        'bold': 'Helvetica-Bold',
        'italic': 'Helvetica-Oblique',
        'bold-italic': 'Helvetica-BoldOblique'
    }
    
    # Color names to RGB
    COLOR_MAP = {
        'black': (0, 0, 0),
        'white': (1, 1, 1),
        'red': (1, 0, 0),
        'green': (0, 1, 0),
        'blue': (0, 0, 1),
        'gray': (0.5, 0.5, 0.5)
    }
    
    def get_font_size(self, css_size: str) -> int:
        """Convert CSS font size to points"""
        # Handle pixel values
        if css_size.endswith('px'):
            try:
                return int(float(css_size[:-2]))
            except:
                return 12
        
        # Handle em values (KISS: assume 1em = 12pt)
        if css_size.endswith('em'):
            try:
                return int(float(css_size[:-2]) * 12)
            except:
                return 12
        
        # Handle named sizes
        return self.FONT_SIZE_MAP.get(css_size, 12)
    
    def get_font_name(self, style: str) -> str:
        """Get PDF font name from style"""
        return self.FONT_MAP.get(style, 'Helvetica')
    
    def get_alignment(self, align: str) -> int:
        """Get PDF alignment constant"""
        align_map = {
            'left': 0,
            'center': 1,
            'right': 2,
            'justify': 4
        }
        return align_map.get(align, 0)
    
    def get_color(self, css_color: str) -> Tuple[float, float, float]:
        """Convert CSS color to RGB tuple"""
        # Handle hex colors
        if css_color.startswith('#'):
            return self._hex_to_rgb(css_color)
        
        # Handle named colors
        return self.COLOR_MAP.get(css_color.lower(), (0, 0, 0))
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[float, float, float]:
        """Convert hex color to RGB"""
        hex_color = hex_color.lstrip('#')
        
        if len(hex_color) == 3:
            # Short form (#RGB)
            hex_color = ''.join([c*2 for c in hex_color])
        
        try:
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            return (r, g, b)
        except:
            return (0, 0, 0)  # Default to black