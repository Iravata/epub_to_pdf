from reportlab.lib.pagesizes import letter, A4, A5
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.platypus import Image as ReportLabImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from pathlib import Path
from typing import Dict, Any, List, Optional
import io

class PDFCreator:
    """Create PDF files using ReportLab (KISS approach)"""
    
    # Page size mapping
    PAGE_SIZES = {
        'letter': letter,
        'A4': A4,
        'A5': A5
    }
    
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.page_size = letter  # Default
        self.margins = (1*inch, 1*inch, 1*inch, 1*inch)  # KISS: Fixed margins
        self.metadata = {}
        self.elements = []  # PDF elements to render
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def set_page_size(self, size: str):
        """Set page size for PDF"""
        self.page_size = self.PAGE_SIZES.get(size, letter)
    
    def set_metadata(self, metadata: Dict[str, str]):
        """Set PDF metadata"""
        self.metadata = metadata
    
    def add_page(self):
        """Add new page to PDF"""
        if self.elements:  # Only if there's content
            self.elements.append(PageBreak())
    
    def add_text(self, text: str, style: str = 'Normal'):
        """Add text paragraph to PDF"""
        if style not in self.styles:
            style = 'Normal'
        
        para = Paragraph(text, self.styles[style])
        self.elements.append(para)
    
    def add_heading(self, text: str, level: int = 1):
        """Add heading to PDF"""
        style_map = {
            1: 'Heading1',
            2: 'Heading2',
            3: 'Heading3',
            4: 'Heading4',
            5: 'Heading5',
            6: 'Heading6'
        }
        style = style_map.get(level, 'Heading1')
        self.add_text(text, style)
        self.add_spacer()
    
    def add_spacer(self, height: float = 0.2):
        """Add vertical space"""
        self.elements.append(Spacer(1, height*inch))
    
    def add_image(self, image_data: bytes, width: Optional[float] = None):
        """Add image to PDF"""
        try:
            # KISS: Simple image addition
            img = ReportLabImage(io.BytesIO(image_data))
            
            if width:
                img.drawWidth = width
                # Maintain aspect ratio
                img.drawHeight = width * img.imageHeight / img.imageWidth
            
            self.elements.append(img)
        except:
            pass  # Skip broken images
    
    def save(self):
        """Save PDF to file"""
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=self.page_size,
            leftMargin=self.margins[0],
            rightMargin=self.margins[1],
            topMargin=self.margins[2],
            bottomMargin=self.margins[3]
        )
        
        # Set metadata
        if self.metadata:
            doc.title = self.metadata.get('title', '')
            doc.author = self.metadata.get('author', '')
            doc.subject = self.metadata.get('subject', '')
        
        # Build PDF
        doc.build(self.elements)
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles (DRY)"""
        # Add custom styles for better formatting
        self.styles.add(ParagraphStyle(
            name='Justified',
            parent=self.styles['Normal'],
            alignment=TA_JUSTIFY
        ))