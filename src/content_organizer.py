import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import re

class ContentOrganizer:
    """Organize EPUB content into structured chapters"""
    
    def __init__(self, epub_path: str):
        self.epub_path = epub_path
        self.book = epub.read_epub(epub_path)
        self._chapters = None
    
    def get_chapters(self) -> List[Dict[str, Any]]:
        """Get ordered list of chapters"""
        if self._chapters is None:
            self._chapters = self._extract_chapters()
        return self._chapters
    
    def get_structure(self) -> Dict[str, Any]:
        """Get hierarchical document structure"""
        chapters = self.get_chapters()
        
        # KISS: Simple flat structure for Phase 2
        return {
            'type': 'book',
            'children': chapters
        }
    
    def _extract_chapters(self) -> List[Dict[str, Any]]:
        """Extract chapters from EPUB"""
        chapters = []
        order = 0
        
        for item in self.book.get_items():
            # Handle both ITEM_DOCUMENT (9) and unknown types with HTML media
            if item.get_type() == ebooklib.ITEM_DOCUMENT or \
               (item.media_type and 'html' in item.media_type.lower()):
                chapter = self._process_chapter(item, order)
                if chapter:
                    chapters.append(chapter)
                    order += 1
        
        return chapters
    
    def _process_chapter(self, item: epub.EpubItem, order: int) -> Dict[str, Any]:
        """Process individual chapter"""
        content = item.get_content().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(content, 'html.parser')
        
        return {
            'id': item.get_id(),
            'name': item.get_name(),
            'order': order,
            'type': self._identify_chapter_type(item, soup),
            'title': self._extract_title(soup, item),
            'content': content  # Keep as HTML for Phase 2
        }
    
    def _identify_chapter_type(self, item: epub.EpubItem, soup: BeautifulSoup) -> str:
        """Identify type of chapter (KISS approach)"""
        name = item.get_name().lower()
        
        if 'cover' in name:
            return 'cover'
        elif 'toc' in name or 'contents' in name:
            return 'toc'
        elif 'appendix' in name or 'glossary' in name:
            return 'appendix'
        else:
            return 'chapter'
    
    def _extract_title(self, soup: BeautifulSoup, item: epub.EpubItem) -> str:
        """Extract chapter title from HTML"""
        # Try common heading tags
        for tag in ['h1', 'h2', 'h3']:
            heading = soup.find(tag)
            if heading:
                return heading.get_text(strip=True)
        
        # Fallback to filename
        return item.get_name().replace('.html', '').replace('_', ' ').title()