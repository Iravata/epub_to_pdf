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
        
        # Escape text to prevent ReportLab parsing errors
        safe_text = self._escape_text_for_reportlab(text)
        para = Paragraph(safe_text, self.styles[style])
        self.elements.append(para)
    
    def add_code(self, code_text: str, preserve_whitespace: bool = True):
        """Add code block to PDF with proper formatting"""
        if not code_text:
            return
        
        # For code blocks, we need to preserve whitespace and formatting
        if preserve_whitespace:
            # Split into lines and preserve structure
            lines = code_text.split('\n')
            
            # Process each line while preserving indentation
            formatted_lines = []
            for line in lines:
                # Replace tabs with spaces for consistent display
                line = line.replace('\t', '    ')
                
                # Only escape the most problematic characters for ReportLab
                line = line.replace('&', '&amp;')
                line = line.replace('<', '&lt;')
                line = line.replace('>', '&gt;')
                
                # Preserve empty lines as actual spaces to maintain structure
                if not line.strip():
                    line = ' '  # Use single space instead of empty line
                
                formatted_lines.append(line)
            
            # Join lines with line breaks that ReportLab understands
            formatted_code = '<br/>'.join(formatted_lines)
        else:
            # Fallback to regular text escaping
            formatted_code = self._escape_text_for_reportlab(code_text)
        
        # Create paragraph with code style
        para = Paragraph(formatted_code, self.styles['Code'])
        self.elements.append(para)
    
    def add_toc_entry(self, title: str, page_num: str = '', level: int = 0):
        """Add a properly formatted TOC entry with dotted leaders"""
        if not title:
            return
        
        # Escape title for ReportLab
        safe_title = self._escape_text_for_reportlab(title)
        
        # Determine style based on level
        if level == 0:
            style_name = 'TOCEntry'
        elif level == 1:
            style_name = 'TOCEntryL1'
        else:
            style_name = 'TOCEntryL2'
        
        # Create formatted entry with dotted leader if page number provided
        if page_num:
            # Better calculation for dotted leader
            base_width = 400  # Approximate page width in points
            indent_width = level * 20
            available_width = base_width - indent_width - 40  # Leave margins
            
            # Estimate text widths (approximate)
            title_width = len(title) * 6.5  # Average character width
            page_width = len(str(page_num)) * 6.5
            
            # Calculate dots needed
            remaining_width = max(20, available_width - title_width - page_width)
            dot_count = max(5, int(remaining_width / 3))  # Minimum 5 dots
            
            # Create the formatted text with proper spacing
            dots = '.' * min(dot_count, 80)  # Limit maximum dots
            formatted_text = f'{safe_title} {dots} {page_num}'
        else:
            formatted_text = safe_title
        
        # Create and add paragraph
        para = Paragraph(formatted_text, self.styles[style_name])
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
        
        # Add code style for monospace text (check if it exists first)
        if 'Code' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='Code',
                parent=self.styles['Normal'],
                fontName='Courier',
                fontSize=9,
                leftIndent=20,
                rightIndent=20,
                spaceAfter=6,
                spaceBefore=6,
                borderWidth=1,
                borderColor='#CCCCCC',
                borderPadding=8,
                backColor='#F8F8F8',
                leading=11  # Line spacing for code
            ))
        else:
            # Modify existing Code style if needed
            code_style = self.styles['Code']
            code_style.fontName = 'Courier'
            code_style.fontSize = 9
            code_style.leftIndent = 20
            code_style.rightIndent = 20
            code_style.borderWidth = 1
            code_style.borderColor = '#CCCCCC'
            code_style.borderPadding = 8
            code_style.backColor = '#F8F8F8'
            code_style.leading = 11
        
        # Improve existing heading styles
        for i in range(1, 7):
            heading_name = f'Heading{i}'
            if heading_name in self.styles:
                heading_style = self.styles[heading_name]
                # Make headings more prominent
                heading_style.fontName = 'Helvetica-Bold'
                heading_style.fontSize = max(18 - i * 2, 10)  # Decreasing sizes
                heading_style.spaceAfter = 12
                heading_style.spaceBefore = 18 if i <= 2 else 12
                heading_style.textColor = '#2C3E50'  # Dark blue-gray
        
        # Improve blockquote style
        if 'Blockquote' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='Blockquote',
                parent=self.styles['Normal'],
                fontName='Times-Italic',
                fontSize=11,
                leftIndent=30,
                rightIndent=30,
                spaceAfter=12,
                spaceBefore=12,
                textColor='#555555'
            ))
        
        # Add TOC styles
        if 'TOCHeading' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='TOCHeading',
                parent=self.styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=16,
                spaceAfter=18,
                spaceBefore=0,
                alignment=TA_LEFT
            ))
        
        if 'TOCEntry' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='TOCEntry',
                parent=self.styles['Normal'],
                fontName='Helvetica',
                fontSize=11,
                spaceAfter=4,
                spaceBefore=1,
                leftIndent=0,
                leading=15,
                fontStyle='normal'
            ))
        
        if 'TOCEntryL1' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='TOCEntryL1',
                parent=self.styles['TOCEntry'],
                leftIndent=20,
                fontSize=10,
                spaceAfter=3,
                textColor='#333333'
            ))
        
        if 'TOCEntryL2' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='TOCEntryL2',
                parent=self.styles['TOCEntry'],
                leftIndent=40,
                fontSize=9,
                spaceAfter=2,
                textColor='#666666'
            ))
    
    def _escape_text_for_reportlab(self, text: str) -> str:
        """Escape text content to prevent ReportLab parsing errors"""
        if not text:
            return text
        
        # Remove or escape HTML tags that ReportLab might try to parse
        import re
        
        # Remove any remaining HTML tags completely
        text = re.sub(r'<[^>]*>', '', text)
        
        # Escape XML/HTML special characters that ReportLab uses for markup
        text = text.replace('&', '&amp;')  # Must be first
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#39;')
        
        # Clean up problematic Unicode characters
        text = text.replace('\xa0', ' ')  # Non-breaking space
        text = text.replace('\u2060', '')  # Word joiner
        text = text.replace('\u200b', '')  # Zero-width space
        text = text.replace('\u2003', ' ')  # Em space
        text = text.replace('\u2002', ' ')  # En space
        text = text.replace('\u2009', ' ')  # Thin space
        
        # Clean up excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text