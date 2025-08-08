import ebooklib
from ebooklib import epub
from typing import List, Dict, Any

class ResourceHandler:
    """Handle EPUB resources (images, styles, etc.)"""
    
    # YAGNI: Only handle what's needed for basic PDF
    SUPPORTED_IMAGE_TYPES = [
        ebooklib.ITEM_IMAGE,
    ]
    
    def __init__(self, epub_path: str):
        self.epub_path = epub_path
        self.book = epub.read_epub(epub_path)
    
    def get_images(self) -> List[Dict[str, Any]]:
        """Extract images from EPUB"""
        images = []
        
        for item in self.book.get_items():
            if item.get_type() in self.SUPPORTED_IMAGE_TYPES:
                image = self._process_image(item)
                if image:
                    images.append(image)
        
        return images
    
    def get_stylesheets(self) -> List[Dict[str, Any]]:
        """Extract CSS stylesheets"""
        styles = []
        
        for item in self.book.get_items():
            if item.get_type() == ebooklib.ITEM_STYLE:
                style = {
                    'name': item.get_name(),
                    'content': item.get_content().decode('utf-8', errors='ignore')
                }
                styles.append(style)
        
        return styles
    
    def get_fonts(self) -> List[Dict[str, Any]]:
        """Get fonts (not implemented in Phase 2 - YAGNI)"""
        return []
    
    def _process_image(self, item: epub.EpubItem) -> Dict[str, Any]:
        """Process individual image"""
        return {
            'name': item.get_name(),
            'data': item.get_content(),
            'mimetype': item.media_type,
            'id': item.get_id()
        }