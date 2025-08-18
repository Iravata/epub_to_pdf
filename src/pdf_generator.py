"""Main PDF generation module integrating all components"""

from pathlib import Path
from typing import Dict, Any, List
import io
import click

from .pdf_creator import PDFCreator
from .html_converter import HTMLToPDFConverter
from .style_mapper import StyleMapper
from .image_embedder import ImageEmbedder

class PDFGenerator:
    """Generate PDF from processed EPUB data (Phase 3 main class)"""
    
    def __init__(self, output_path: str, page_size: str = 'letter'):
        self.output_path = output_path
        self.pdf_creator = PDFCreator(output_path)
        self.pdf_creator.set_page_size(page_size)
        
        self.html_converter = HTMLToPDFConverter()
        self.style_mapper = StyleMapper()
        self.image_embedder = ImageEmbedder()
        
        self.image_cache = {}  # Cache processed images
    
    def generate(self, epub_data: Dict[str, Any]) -> bool:
        """Generate PDF from EPUB data"""
        try:
            # Set metadata
            self._add_metadata(epub_data['metadata'])
            
            # Cache images for quick lookup
            self._cache_images(epub_data.get('images', []))
            
            # Process chapters
            for i, chapter in enumerate(epub_data['chapters']):
                if i > 0:
                    self.pdf_creator.add_page()  # New page for each chapter
                
                self._process_chapter(chapter)
            
            # Save PDF
            self.pdf_creator.save()
            return True
            
        except Exception as e:
            click.echo(f"PDF generation error: {e}", err=True)
            return False
    
    def _add_metadata(self, metadata: Dict[str, Any]):
        """Add metadata to PDF"""
        pdf_metadata = {
            'title': str(metadata.get('title', 'Untitled')),
            'author': str(metadata.get('author', 'Unknown')),
            'subject': str(metadata.get('description', ''))[:100]  # Limit length
        }
        self.pdf_creator.set_metadata(pdf_metadata)
    
    def _cache_images(self, images: List[Dict[str, Any]]):
        """Cache processed images for embedding"""
        for img in images:
            processed = self.image_embedder.prepare_image(
                img['data'],
                max_width=400  # KISS: Fixed max width
            )
            if processed:
                self.image_cache[img['name']] = processed
    
    def _process_chapter(self, chapter: Dict[str, Any]):
        """Process individual chapter"""
        # Convert HTML content to PDF elements first to check for headings
        elements = self.html_converter.convert(chapter['content'])
        
        # Check if the first element is already a heading that matches the chapter title
        chapter_title = chapter.get('title', '').strip()
        has_matching_heading = False
        
        if elements and chapter_title:
            first_element = elements[0]
            if (first_element.get('type') == 'heading' and 
                first_element.get('text', '').strip().lower() == chapter_title.lower()):
                has_matching_heading = True
        
        # Only add chapter title if it's not already present in the content
        if chapter_title and not has_matching_heading:
            self.pdf_creator.add_heading(chapter_title, level=1)
        
        # Add elements to PDF
        for element in elements:
            self._add_element(element)
    
    def _add_element(self, element: Dict[str, Any]):
        """Add individual element to PDF"""
        elem_type = element.get('type')
        
        if elem_type == 'paragraph':
            self._add_paragraph(element)
        elif elem_type == 'heading':
            self._add_heading(element)
        elif elem_type == 'list':
            self._add_list(element)
        elif elem_type == 'image':
            self._add_image(element)
        elif elem_type == 'blockquote':
            self._add_blockquote(element)
        elif elem_type == 'break':
            self.pdf_creator.add_spacer(0.1)
        elif elem_type == 'text':
            self.pdf_creator.add_text(element['text'], 'Normal')
        elif elem_type == 'code':
            self._add_code(element)
        elif elem_type == 'table':
            self._add_table(element)
    
    def _add_paragraph(self, element: Dict[str, Any]):
        """Add paragraph to PDF"""
        text = element.get('text', '')
        if text:
            # Use justified alignment for better readability
            style = 'Justified' if 'Justified' in self.pdf_creator.styles else 'Normal'
            self.pdf_creator.add_text(text, style)
            self.pdf_creator.add_spacer(0.1)
    
    def _add_heading(self, element: Dict[str, Any]):
        """Add heading to PDF"""
        text = element.get('text', '')
        level = element.get('level', 1)
        if text:
            self.pdf_creator.add_heading(text, level)
    
    def _add_list(self, element: Dict[str, Any]):
        """Add list to PDF"""
        items = element.get('items', [])
        ordered = element.get('ordered', False)
        
        for i, item in enumerate(items):
            if ordered:
                bullet = f"{i+1}. {item}"
            else:
                bullet = f"• {item}"
            
            self.pdf_creator.add_text(bullet, 'Normal')
        
        self.pdf_creator.add_spacer(0.1)
    
    def _add_image(self, element: Dict[str, Any]):
        """Add image to PDF"""
        src = element.get('src', '')
        if not src:
            return
        
        # Normalize the src path - remove relative path components
        normalized_src = src.replace('../../', '').replace('../', '').replace('./', '')
        
        # Look for image in cache with improved matching
        for name, img_data in self.image_cache.items():
            # Normalize the cached name too
            normalized_name = name.replace('../../', '').replace('../', '').replace('./', '')
            
            # Try multiple matching strategies
            if (normalized_src == normalized_name or 
                normalized_src in normalized_name or 
                normalized_name in normalized_src or
                normalized_src.split('/')[-1] == normalized_name.split('/')[-1]):  # Match just filename
                
                try:
                    self.pdf_creator.add_image(
                        img_data['data'],
                        width=img_data['width'] * 0.75  # Scale to fit
                    )
                    self.pdf_creator.add_spacer(0.2)
                    break
                except Exception as e:
                    # Silently skip failed images
                    continue
    
    def _add_blockquote(self, element: Dict[str, Any]):
        """Add blockquote to PDF"""
        text = element.get('text', '')
        if text:
            # Use custom blockquote style if available
            style = 'Blockquote' if 'Blockquote' in self.pdf_creator.styles else 'Italic'
            self.pdf_creator.add_text(text, style)
    
    def _add_code(self, element: Dict[str, Any]):
        """Add code block to PDF"""
        text = element.get('text', '')
        if text:
            # Use the new code formatting method
            preserve_whitespace = element.get('preserve_whitespace', True)
            self.pdf_creator.add_code(text, preserve_whitespace)
            self.pdf_creator.add_spacer(0.1)
    
    def _add_table(self, element: Dict[str, Any]):
        """Add table to PDF"""
        text = element.get('text', '')
        if text:
            # Simple table representation as formatted text
            self.pdf_creator.add_text(text, 'Normal')
            self.pdf_creator.add_spacer(0.15)