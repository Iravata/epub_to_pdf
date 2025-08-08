import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import xml.etree.ElementTree as ET

class NavigationParser:
    """Parse EPUB navigation (TOC)"""
    
    def __init__(self, epub_path: str):
        self.epub_path = epub_path
        self.book = epub.read_epub(epub_path)
    
    def parse_toc(self) -> List[Dict[str, Any]]:
        """Parse table of contents from EPUB"""
        # Try NCX first (EPUB 2)
        toc = self._parse_ncx()
        
        # Try NAV if NCX not found (EPUB 3)
        if not toc:
            toc = self._parse_nav()
        
        # Generate from headings as fallback
        if not toc:
            toc = self._generate_from_headings()
        
        return toc
    
    def _parse_ncx(self) -> List[Dict[str, Any]]:
        """Parse NCX navigation (EPUB 2)"""
        toc = []
        
        for item in self.book.get_items():
            if item.get_type() == ebooklib.ITEM_NAVIGATION:
                content = item.get_content().decode('utf-8', errors='ignore')
                toc = self._extract_ncx_toc(content)
                break
        
        return toc
    
    def _extract_ncx_toc(self, ncx_content: str) -> List[Dict[str, Any]]:
        """Extract TOC from NCX content"""
        toc = []
        
        try:
            root = ET.fromstring(ncx_content)
            # Define namespace
            ns = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}
            
            # Find all navPoints
            for navpoint in root.findall('.//ncx:navPoint', ns):
                entry = self._parse_navpoint(navpoint, ns, level=0)
                if entry:
                    toc.append(entry)
        except:
            pass
        
        return toc
    
    def _parse_navpoint(self, navpoint, ns: dict, level: int) -> Dict[str, Any]:
        """Parse individual navPoint"""
        # KISS: Simple extraction
        text_elem = navpoint.find('.//ncx:text', ns)
        content_elem = navpoint.find('.//ncx:content', ns)
        
        if text_elem is not None and content_elem is not None:
            entry = {
                'title': text_elem.text,
                'href': content_elem.get('src', ''),
                'level': level
            }
            
            # Check for children (DRY: reuse same method)
            children = []
            for child in navpoint.findall('ncx:navPoint', ns):
                child_entry = self._parse_navpoint(child, ns, level + 1)
                if child_entry:
                    children.append(child_entry)
            
            if children:
                entry['children'] = children
            
            return entry
        
        return None
    
    def _parse_nav(self) -> List[Dict[str, Any]]:
        """Parse NAV document (EPUB 3)"""
        # YAGNI: Implement only if needed in testing
        return []
    
    def _generate_from_headings(self) -> List[Dict[str, Any]]:
        """Generate TOC from HTML headings as fallback"""
        toc = []
        
        for item in self.book.get_items():
            # Handle both ITEM_DOCUMENT and unknown types with HTML media
            if item.get_type() == ebooklib.ITEM_DOCUMENT or \
               (item.media_type and 'html' in item.media_type.lower()):
                content = item.get_content().decode('utf-8', errors='ignore')
                soup = BeautifulSoup(content, 'html.parser')
                
                # Find first heading
                for tag in ['h1', 'h2', 'h3']:
                    heading = soup.find(tag)
                    if heading:
                        toc.append({
                            'title': heading.get_text(strip=True),
                            'href': item.get_name(),
                            'level': int(tag[1]) - 1,
                            'generated': True
                        })
                        break
        
        return toc