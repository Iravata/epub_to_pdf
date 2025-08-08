from ebooklib import epub
from datetime import datetime
from typing import Dict, Any, List, Optional

class MetadataParser:
    """Parse and normalize EPUB metadata"""
    
    # DRY: Define metadata mapping once
    METADATA_MAPPING = {
        'title': ('DC', 'title'),
        'creator': ('DC', 'creator'),
        'language': ('DC', 'language'),
        'publisher': ('DC', 'publisher'),
        'date': ('DC', 'date'),
        'identifier': ('DC', 'identifier'),
        'description': ('DC', 'description'),
        'subject': ('DC', 'subject'),
        'rights': ('DC', 'rights'),
    }
    
    def __init__(self, epub_path: str):
        self.epub_path = epub_path
        self.book = epub.read_epub(epub_path)
    
    def parse(self) -> Dict[str, Any]:
        """Parse all metadata from EPUB"""
        metadata = {}
        
        # DRY: Use mapping to avoid repetition
        for field, (namespace, name) in self.METADATA_MAPPING.items():
            value = self._get_metadata_value(namespace, name)
            metadata[self._normalize_field_name(field)] = value
        
        # KISS: Simple post-processing
        metadata = self._post_process_metadata(metadata)
        
        return metadata
    
    def _get_metadata_value(self, namespace: str, name: str) -> Optional[Any]:
        """Get metadata value with proper error handling"""
        try:
            values = self.book.get_metadata(namespace, name)
            if not values:
                return None
            
            # Return single value or list based on count
            if len(values) == 1:
                return values[0][0] if values[0] else None
            else:
                return [v[0] for v in values if v]
        except:
            return None
    
    def _normalize_field_name(self, field: str) -> str:
        """Normalize field names for consistency"""
        mapping = {
            'creator': 'author',
            'date': 'publication_date',
            'identifier': 'isbn',
            'subject': 'genres'
        }
        return mapping.get(field, field)
    
    def _post_process_metadata(self, metadata: Dict) -> Dict:
        """Post-process metadata with defaults"""
        # KISS: Simple defaults
        metadata['title'] = metadata.get('title') or 'Untitled'
        metadata['author'] = metadata.get('author') or 'Unknown Author'
        metadata['language'] = metadata.get('language') or 'en'
        
        # Parse date if present
        if metadata.get('publication_date'):
            metadata['publication_date'] = self._parse_date(
                metadata['publication_date']
            )
        
        return metadata
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to standard format"""
        # KISS: Just return as-is for now
        return date_str