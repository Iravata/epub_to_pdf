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
        # Add chapter title if present
        if chapter.get('title'):
            self.pdf_creator.add_heading(chapter['title'], level=1)
        
        # Convert HTML content to PDF elements
        elements = self.html_converter.convert(chapter['content'])
        
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
            self.pdf_creator.add_text(element['text'])
    
    def _add_paragraph(self, element: Dict[str, Any]):
        """Add paragraph to PDF"""
        text = element.get('text', '')
        if text:
            # KISS: Use default style for now
            self.pdf_creator.add_text(text, 'Normal')
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
        
        # Look for image in cache
        for name, img_data in self.image_cache.items():
            if src in name or name in src:
                self.pdf_creator.add_image(
                    img_data['data'],
                    width=img_data['width'] * 0.75  # Scale to fit
                )
                self.pdf_creator.add_spacer(0.2)
                break
    
    def _add_blockquote(self, element: Dict[str, Any]):
        """Add blockquote to PDF"""
        text = element.get('text', '')
        if text:
            # KISS: Use italic style for blockquotes
            self.pdf_creator.add_text(f'"{text}"', 'Italic')
            self.pdf_creator.add_spacer(0.15)