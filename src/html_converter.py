from bs4 import BeautifulSoup, NavigableString
from typing import List, Dict, Any, Optional
import re

class HTMLToPDFConverter:
    """Convert HTML content to PDF elements (KISS approach)"""
    
    def __init__(self):
        # Element type mapping
        self.element_mapping = {
            'p': 'paragraph',
            'h1': 'heading',
            'h2': 'heading',
            'h3': 'heading',
            'h4': 'heading',
            'h5': 'heading',
            'h6': 'heading',
            'ul': 'list',
            'ol': 'list',
            'img': 'image',
            'blockquote': 'blockquote',
            'pre': 'code'
        }
    
    def convert(self, html: str) -> List[Dict[str, Any]]:
        """Convert HTML to PDF element list"""
        soup = BeautifulSoup(html, 'html.parser')
        elements = []
        
        # Process body or entire content
        content = soup.body if soup.body else soup
        
        for element in content.children:
            if isinstance(element, NavigableString):
                # Handle text nodes
                text = str(element).strip()
                if text:
                    elements.append({
                        'type': 'text',
                        'text': text
                    })
            else:
                # Handle HTML elements
                pdf_element = self._convert_element(element)
                if pdf_element:
                    elements.append(pdf_element)
        
        return elements
    
    def _convert_element(self, element) -> Optional[Dict[str, Any]]:
        """Convert individual HTML element"""
        tag_name = element.name.lower() if element.name else ''
        
        if tag_name in ['p', 'div']:
            return self._convert_paragraph(element)
        elif tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return self._convert_heading(element)
        elif tag_name in ['ul', 'ol']:
            return self._convert_list(element)
        elif tag_name == 'img':
            return self._convert_image(element)
        elif tag_name == 'blockquote':
            return self._convert_blockquote(element)
        elif tag_name == 'br':
            return {'type': 'break'}
        else:
            # Default to text extraction
            text = element.get_text(strip=True)
            if text:
                return {'type': 'text', 'text': text}
        
        return None
    
    def _convert_paragraph(self, element) -> Dict[str, Any]:
        """Convert paragraph element"""
        return {
            'type': 'paragraph',
            'text': self._extract_formatted_text(element),
            'styles': self._extract_styles(element)
        }
    
    def _convert_heading(self, element) -> Dict[str, Any]:
        """Convert heading element"""
        level = int(element.name[1])  # h1 -> 1, h2 -> 2, etc.
        return {
            'type': 'heading',
            'level': level,
            'text': element.get_text(strip=True)
        }
    
    def _convert_list(self, element) -> Dict[str, Any]:
        """Convert list element"""
        items = []
        for li in element.find_all('li', recursive=False):
            items.append(li.get_text(strip=True))
        
        return {
            'type': 'list',
            'ordered': element.name == 'ol',
            'items': items
        }
    
    def _convert_image(self, element) -> Dict[str, Any]:
        """Convert image element"""
        return {
            'type': 'image',
            'src': element.get('src', ''),
            'alt': element.get('alt', ''),
            'width': element.get('width'),
            'height': element.get('height')
        }
    
    def _convert_blockquote(self, element) -> Dict[str, Any]:
        """Convert blockquote element"""
        return {
            'type': 'blockquote',
            'text': element.get_text(strip=True)
        }
    
    def _extract_formatted_text(self, element) -> str:
        """Extract text with inline formatting preserved"""
        # KISS: Just get text for now, handle formatting in Phase 4
        return element.get_text(strip=True)
    
    def _extract_styles(self, element) -> Dict[str, Any]:
        """Extract style information from element"""
        styles = {}
        
        # Check for common inline styles
        style_attr = element.get('style', '')
        if style_attr:
            # KISS: Parse only essential styles
            if 'text-align' in style_attr:
                match = re.search(r'text-align:\s*(\w+)', style_attr)
                if match:
                    styles['align'] = match.group(1)
            
            if 'color' in style_attr:
                match = re.search(r'color:\s*([^;]+)', style_attr)
                if match:
                    styles['color'] = match.group(1).strip()
        
        return styles