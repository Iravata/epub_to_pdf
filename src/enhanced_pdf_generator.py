"""Enhanced PDF generator with Phase 4 features"""

from pathlib import Path
from typing import Dict, Any, List

from .pdf_generator import PDFGenerator
from .css_processor import CSSProcessor
from .toc_generator import TOCGenerator
from .font_handler import FontHandler
from .page_layout import PageLayout
from .html_sanitizer import HTMLSanitizer

class EnhancedPDFGenerator(PDFGenerator):
    """Enhanced PDF generator with advanced features"""
    
    def __init__(self, output_path: str, options: Dict[str, Any] = None):
        super().__init__(output_path)
        
        self.options = options or {}
        
        # Initialize advanced components
        self.css_processor = CSSProcessor()
        self.toc_generator = TOCGenerator()
        self.font_handler = FontHandler()
        self.page_layout = PageLayout()
        self.html_sanitizer = HTMLSanitizer()
        
        # Configure from options
        self._configure_layout()
    
    def generate(self, epub_data: Dict[str, Any]) -> bool:
        """Generate enhanced PDF from EPUB data"""
        try:
            # Process CSS styles
            self._process_styles(epub_data.get('styles', []))
            
            # Set metadata
            self._add_metadata(epub_data['metadata'])
            
            # Generate TOC if available
            if epub_data.get('toc'):
                self._add_table_of_contents(epub_data['toc'])
            
            # Cache images
            self._cache_images(epub_data.get('images', []))
            
            # Process chapters with styles
            for i, chapter in enumerate(epub_data['chapters']):
                if i > 0:
                    self.pdf_creator.add_page()
                
                self._process_chapter_with_styles(chapter)
            
            # Save PDF
            self.pdf_creator.save()
            
            # Add bookmarks (post-processing)
            if epub_data.get('toc'):
                self._add_bookmarks(epub_data['toc'])
            
            return True
            
        except Exception as e:
            print(f"Enhanced PDF generation error: {e}")
            return False
    
    def _configure_layout(self):
        """Configure page layout from options"""
        # Set margins if provided
        if 'margins' in self.options:
            margins = self.options['margins']
            self.page_layout.set_margins(**margins)
            
            # Apply to PDF creator
            self.pdf_creator.margins = (
                self.page_layout.margins['left'],
                self.page_layout.margins['right'],
                self.page_layout.margins['top'],
                self.page_layout.margins['bottom']
            )
        
        # Set page numbers if requested
        if self.options.get('page_numbers'):
            self.page_layout.enable_page_numbers()
        
        # Set header/footer if provided
        if 'header' in self.options:
            self.page_layout.set_header(self.options['header'])
        
        if 'footer' in self.options:
            self.page_layout.set_footer(self.options['footer'])
    
    def _process_styles(self, styles: List[Dict[str, str]]):
        """Process and store CSS styles"""
        self.css_rules = {}
        
        for style in styles:
            css_content = style.get('content', '')
            rules = self.css_processor.parse_stylesheet(css_content)
            self.css_rules.update(rules)
            
            # Detect fonts
            fonts = self.font_handler.detect_fonts(css_content)
            # Fonts would be registered here if we had TTF files
    
    def _add_table_of_contents(self, toc_data: List[Dict[str, Any]]):
        """Add TOC page to PDF with improved formatting"""
        # Add TOC title
        self.pdf_creator.add_text('Table of Contents', 'TOCHeading')
        self.pdf_creator.add_spacer(0.3)
        
        # Add TOC entries with proper formatting
        page_counter = 1  # Simple page numbering for demo
        
        for entry in toc_data:
            title = entry.get('title', '').strip()
            level = entry.get('level', 0)
            
            if title:
                # Generate page number (simplified - in real implementation would track actual pages)
                page_num = str(page_counter)
                page_counter += 1
                
                # Add formatted TOC entry
                self.pdf_creator.add_toc_entry(title, page_num, level)
        
        # Add some space after TOC
        self.pdf_creator.add_spacer(0.5)
        self.pdf_creator.add_page()
    
    def _process_chapter_with_styles(self, chapter: Dict[str, Any]):
        """Process chapter with CSS styles applied"""
        # Apply stored CSS to chapter HTML if preserve_styles is enabled
        if self.options.get('preserve_styles', True):
            styled_html = self.css_processor.apply_styles(
                chapter['content'],
                self._css_rules_to_string()
            )
            
            # Sanitize the styled HTML to prevent parsing issues
            styled_html = self.html_sanitizer.sanitize(styled_html)
            
            # Update chapter content
            chapter['content'] = styled_html
        
        # Process as normal
        self._process_chapter(chapter)
    
    def _css_rules_to_string(self) -> str:
        """Convert CSS rules dict to string"""
        css_parts = []
        for selector, rules in getattr(self, 'css_rules', {}).items():
            rule_str = '; '.join([f'{k}: {v}' for k, v in rules.items()])
            css_parts.append(f"{selector} {{ {rule_str} }}")
        
        return '\n'.join(css_parts)
    
    def _add_bookmarks(self, toc_data: List[Dict[str, Any]]):
        """Add PDF bookmarks"""
        # Convert TOC to bookmark format
        bookmarks = []
        page = 1  # Track current page
        
        for entry in toc_data:
            bookmarks.append({
                'title': entry.get('title', ''),
                'page': page,
                'children': []  # Could be extended for nested TOC
            })
            page += 1  # Simplified page tracking
        
        # Add to PDF
        self.toc_generator.add_bookmarks(self.output_path, bookmarks)
    
    def _add_element(self, element: Dict[str, Any]):
        """Override to handle TOC elements"""
        elem_type = element.get('type')
        
        if elem_type == 'toc_entry':
            self._add_toc_entry(element)
        else:
            # Use parent implementation
            super()._add_element(element)
    
    def _add_toc_entry(self, element: Dict[str, Any]):
        """Add TOC entry to PDF with improved formatting"""
        title = element.get('title', '')
        page = element.get('page', '')
        level = element.get('level', 0)
        
        if title:
            # Use the new TOC entry method
            self.pdf_creator.add_toc_entry(title, page, level)
