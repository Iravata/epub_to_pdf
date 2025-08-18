from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import letter, A4
from typing import Dict, Any, Optional, Tuple

class PageLayout:
    """Manage page layout settings for PDF"""
    
    def __init__(self):
        self.margins = {
            'top': 1 * inch,
            'right': 1 * inch,
            'bottom': 1 * inch,
            'left': 1 * inch
        }
        
        self.header = None
        self.footer = None
        self.page_numbers = None
        self.columns = 1
        self.column_gap = 0.5 * inch
        
        # Page size
        self.page_size = letter
    
    def set_margins(self, top: float = None, right: float = None,
                   bottom: float = None, left: float = None):
        """Set page margins in inches"""
        if top is not None:
            self.margins['top'] = top * inch
        if right is not None:
            self.margins['right'] = right * inch
        if bottom is not None:
            self.margins['bottom'] = bottom * inch
        if left is not None:
            self.margins['left'] = left * inch
    
    def get_margins(self) -> Dict[str, float]:
        """Get margins in inches"""
        return {
            'top': self.margins['top'] / inch,
            'right': self.margins['right'] / inch,
            'bottom': self.margins['bottom'] / inch,
            'left': self.margins['left'] / inch
        }
    
    def set_header(self, text: str, align: str = 'center'):
        """Set page header"""
        self.header = {
            'text': text,
            'align': align
        }
    
    def set_footer(self, text: str, align: str = 'center'):
        """Set page footer"""
        self.footer = {
            'text': text,
            'align': align
        }
    
    def has_header(self) -> bool:
        """Check if header is set"""
        return self.header is not None
    
    def has_footer(self) -> bool:
        """Check if footer is set"""
        return self.footer is not None
    
    def enable_page_numbers(self, position: str = 'bottom-right',
                           format: str = '{page}',
                           start_page: int = 1):
        """Enable page numbering"""
        self.page_numbers = {
            'position': position,
            'format': format,
            'start_page': start_page,
            'current_page': start_page
        }
    
    def page_numbering_enabled(self) -> bool:
        """Check if page numbering is enabled"""
        return self.page_numbers is not None
    
    def set_columns(self, count: int, gap: float = 0.5):
        """Set multi-column layout"""
        self.columns = max(1, count)
        self.column_gap = gap * inch
    
    def get_column_count(self) -> int:
        """Get number of columns"""
        return self.columns
    
    def get_column_gap(self) -> float:
        """Get column gap in inches"""
        return self.column_gap / inch
    
    def get_content_width(self) -> float:
        """Get available content width"""
        page_width = self.page_size[0]
        return page_width - self.margins['left'] - self.margins['right']
    
    def get_content_height(self) -> float:
        """Get available content height"""
        page_height = self.page_size[1]
        height = page_height - self.margins['top'] - self.margins['bottom']
        
        # Account for header/footer
        if self.header:
            height -= 0.5 * inch
        if self.footer:
            height -= 0.5 * inch
        
        return height
    
    def get_column_width(self) -> float:
        """Get width of each column"""
        if self.columns <= 1:
            return self.get_content_width()
        
        total_gap = self.column_gap * (self.columns - 1)
        return (self.get_content_width() - total_gap) / self.columns
