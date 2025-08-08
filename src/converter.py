"""Main converter module integrating all Phase 2 components"""

from pathlib import Path
from typing import Dict, Any

from .epub_validator import EPUBValidator
from .metadata_parser import MetadataParser
from .content_organizer import ContentOrganizer
from .navigation_parser import NavigationParser
from .resource_handler import ResourceHandler

class EPUBProcessor:
    """Process EPUB files (Phase 2 main class)"""
    
    def __init__(self, epub_path: str):
        self.epub_path = epub_path
        
        # Validate first
        validator = EPUBValidator(epub_path)
        if not validator.is_valid():
            raise ValueError(f"Invalid EPUB: {validator.get_error()}")
        
        # Initialize components (DRY: single initialization)
        self.metadata_parser = MetadataParser(epub_path)
        self.content_organizer = ContentOrganizer(epub_path)
        self.navigation_parser = NavigationParser(epub_path)
        self.resource_handler = ResourceHandler(epub_path)
    
    def process(self) -> Dict[str, Any]:
        """Process EPUB and return structured data"""
        return {
            'metadata': self.metadata_parser.parse(),
            'chapters': self.content_organizer.get_chapters(),
            'structure': self.content_organizer.get_structure(),
            'toc': self.navigation_parser.parse_toc(),
            'images': self.resource_handler.get_images(),
            'styles': self.resource_handler.get_stylesheets()
        }