from pathlib import Path
import zipfile
from ebooklib import epub
import ebooklib

class EPUBExtractor:
    """Basic EPUB content extractor (YAGNI - only essentials)"""
    
    def __init__(self, filepath):
        self.filepath = Path(filepath)
    
    def extract(self):
        """Extract basic structure from EPUB"""
        if not self.filepath.exists():
            raise FileNotFoundError(f"File not found: {self.filepath}")
        
        try:
            book = epub.read_epub(self.filepath)
            
            # Extract only essential metadata (YAGNI)
            metadata = {
                'title': book.get_metadata('DC', 'title'),
                'author': book.get_metadata('DC', 'creator'),
            }
            
            # Get list of content files
            content_files = []
            for item in book.get_items():
                # Check for HTML/XHTML documents
                if item.get_type() in [ebooklib.ITEM_DOCUMENT, ebooklib.ITEM_NAVIGATION]:
                    content_files.append(item.get_name())
                # Also check by media type if type is not set
                elif hasattr(item, 'media_type') and 'html' in item.media_type.lower():
                    content_files.append(item.get_name())
            
            return {
                'metadata': metadata,
                'content_files': content_files
            }
        except Exception as e:
            raise ValueError(f"Failed to extract EPUB: {e}")