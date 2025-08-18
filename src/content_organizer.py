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
        """Extract chapters from EPUB with deduplication"""
        chapters = []
        order = 0
        seen_titles = set()  # Track chapter titles to prevent duplicates
        
        for item in self.book.get_items():
            # Handle both ITEM_DOCUMENT (9) and unknown types with HTML media
            if item.get_type() == ebooklib.ITEM_DOCUMENT or \
               (item.media_type and 'html' in item.media_type.lower()):
                chapter = self._process_chapter(item, order)
                if chapter and self._should_include_chapter(chapter, seen_titles):
                    chapters.append(chapter)
                    seen_titles.add(chapter['title'].lower())
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
    
    def _should_include_chapter(self, chapter: Dict[str, Any], seen_titles: set) -> bool:
        """Determine if chapter should be included (avoid duplicates and unwanted content)"""
        title = chapter['title'].lower()
        chapter_type = chapter['type']
        name = chapter['name'].lower()
        
        # Skip if we've already seen this title (exact match)
        if title in seen_titles:
            return False
        
        # Skip if we've seen a very similar title (fuzzy matching)
        for seen_title in seen_titles:
            if self._titles_are_similar(title, seen_title):
                return False
        
        # Skip certain types of content that are usually redundant
        skip_patterns = [
            'titlepage',
            'toc.',  # Skip standalone TOC files (we generate our own)
            'btoc.',  # Skip brief TOC files
            'nav.',   # Skip navigation files
            'cover',  # Skip cover pages after the first
        ]
        
        for pattern in skip_patterns:
            if pattern in name:
                return False
        
        # Skip chapters with empty or very short content
        content = chapter.get('content', '')
        if len(content.strip()) < 100:  # Skip very short content
            return False
        
        # Include everything else
        return True
    
    def _titles_are_similar(self, title1: str, title2: str) -> bool:
        """Check if two titles are similar enough to be considered duplicates"""
        # Remove common words and punctuation for comparison
        import re
        
        def normalize_title(title):
            # Remove punctuation and extra spaces, convert to lowercase
            cleaned = re.sub(r'[^\w\s]', '', title.lower())
            # Remove common words
            words = cleaned.split()
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            meaningful_words = [w for w in words if w not in common_words and len(w) > 2]
            return ' '.join(sorted(meaningful_words))
        
        norm1 = normalize_title(title1)
        norm2 = normalize_title(title2)
        
        # Consider similar if normalized titles are the same or one contains the other
        if norm1 == norm2:
            return True
        
        if norm1 and norm2 and (norm1 in norm2 or norm2 in norm1):
            return True
        
        return False