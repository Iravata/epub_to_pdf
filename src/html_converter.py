from bs4 import BeautifulSoup, NavigableString
from typing import List, Dict, Any, Optional
import re
from .html_sanitizer import HTMLSanitizer

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
        
        # Initialize HTML sanitizer
        self.sanitizer = HTMLSanitizer()
        
        # Track processed content to prevent duplicates
        self.processed_content = set()
        self.processed_elements = set()  # Track processed element objects
    
    def convert(self, html: str) -> List[Dict[str, Any]]:
        """Convert HTML to PDF element list"""
        # Reset content tracking for each conversion
        self.processed_content.clear()
        self.processed_elements.clear()
        
        # Sanitize HTML first to handle malformed content
        sanitized_html = self.sanitizer.sanitize(html)
        soup = BeautifulSoup(sanitized_html, 'html.parser')
        elements = []
        
        # Find the main content container
        content = soup.body if soup.body else soup
        
        # If there's a specific content div, use that (prioritize inner content)
        content_div = soup.find('div', {'id': 'sbo-rt-content'}) or \
                     soup.find('div', {'class': 'calibre'}) or \
                     soup.find('div', {'id': 'book-content'}) or \
                     soup.find('div', {'class': 'content'})
        
        if content_div:
            content = content_div
        
        # Process all elements recursively to maintain structure
        self._process_elements_recursive(content, elements)
        
        return self._deduplicate_elements(elements)
    
    def _process_elements_recursive(self, container, elements: List[Dict[str, Any]]):
        """Recursively process HTML elements maintaining structure"""
        for element in container.children:
            if isinstance(element, NavigableString):
                # Handle text nodes - only add if there's significant content
                text = str(element).strip()
                if text and len(text) > 2:  # Skip tiny fragments
                    elements.append({
                        'type': 'text',
                        'text': self._sanitize_text_content(text)
                    })
            else:
                # Skip if this element was already processed
                element_id = id(element)
                if element_id in self.processed_elements:
                    continue
                
                # Handle HTML elements
                tag_name = element.name.lower() if element.name else ''
                
                if tag_name == 'img':
                    # Handle direct images
                    img_elem = self._convert_image(element)
                    if img_elem:
                        elements.append(img_elem)
                        
                elif tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    # Handle headings
                    heading_text = element.get_text(strip=True)
                    if heading_text:
                        level = int(tag_name[1])
                        elements.append({
                            'type': 'heading',
                            'level': level,
                            'text': self._sanitize_text_content(heading_text)
                        })
                        # Mark this heading as processed to prevent duplication
                        self.processed_elements.add(id(element))
                        
                elif tag_name in ['ul', 'ol']:
                    # Handle lists
                    list_elem = self._convert_list(element)
                    if list_elem and list_elem.get('items'):
                        elements.append(list_elem)
                        self.processed_elements.add(id(element))
                        
                elif tag_name == 'blockquote':
                    # Handle blockquotes
                    quote_text = element.get_text(strip=True)
                    if quote_text:
                        elements.append({
                            'type': 'blockquote',
                            'text': self._sanitize_text_content(quote_text)
                        })
                        self.processed_elements.add(id(element))
                        
                elif tag_name == 'br':
                    # Handle line breaks
                    elements.append({'type': 'break'})
                    
                elif tag_name in ['pre', 'code']:
                    # Handle code blocks with preserved formatting
                    code_text = self._extract_code_text(element)
                    if code_text.strip():
                        classes = element.get('class', [])
                        elements.append({
                            'type': 'code',
                            'text': code_text,
                            'language': self._detect_code_language(classes),
                            'preserve_whitespace': True
                        })
                        self.processed_elements.add(id(element))
                        
                elif tag_name in ['table']:
                    # Handle tables (simplified)
                    table_elem = self._convert_table(element)
                    if table_elem:
                        elements.append(table_elem)
                        self.processed_elements.add(id(element))
                        
                elif tag_name in ['p', 'div']:
                    # Check if this is a code block first
                    classes = element.get('class', [])
                    styles = self._parse_style_string(element.get('style', ''))
                    
                    if self._is_code_element(element.name, classes, styles):
                        # Handle as code block with preserved formatting
                        code_text = self._extract_code_text(element)
                        if code_text.strip():
                            elements.append({
                                'type': 'code',
                                'text': code_text,
                                'language': self._detect_code_language(classes),
                                'preserve_whitespace': True
                            })
                            self.processed_elements.add(id(element))
                    else:
                        # Process as regular paragraph/div
                        paragraph_text = self._extract_paragraph_text(element)
                        if paragraph_text.strip():
                            elements.append({
                                'type': 'paragraph',
                                'text': paragraph_text,
                                'styles': self._extract_styles(element)
                            })
                            self.processed_elements.add(id(element))
                        
                        # Only process children recursively if we didn't extract text content
                        # This prevents duplicate processing
                        if not paragraph_text.strip() and hasattr(element, 'children'):
                            self._process_elements_recursive(element, elements)
                        
                else:
                    # Check for nested images in other elements  
                    img_tags = element.find_all('img') if hasattr(element, 'find_all') else []
                    for img in img_tags:
                        img_elem = self._convert_image(img)
                        if img_elem:
                            elements.append(img_elem)
                    
                    # For other elements, process children recursively
                    if hasattr(element, 'children'):
                        self._process_elements_recursive(element, elements)
    
    def _extract_paragraph_text(self, element) -> str:
        """Extract text from paragraph while preserving inline formatting"""
        texts = []
        
        # Only process direct children and their text, not nested block elements
        for child in element.children:
            if isinstance(child, NavigableString):
                text = str(child).strip()
                if text:
                    texts.append(text)
            elif hasattr(child, 'name'):
                if child.name in ['br']:
                    texts.append(' ')
                elif child.name in ['a', 'span', 'em', 'strong', 'b', 'i', 'code']:
                    # Inline elements - extract their text
                    inline_text = child.get_text(strip=True)
                    if inline_text:
                        texts.append(inline_text)
                # Skip nested block elements like p, div, h1-h6, etc.
        
        # Join and clean up the text
        paragraph_text = ' '.join(texts)
        return self._sanitize_text_content(paragraph_text)
    
    def _convert_table(self, element) -> Optional[Dict[str, Any]]:
        """Convert table to a simple text representation"""
        rows = []
        for tr in element.find_all('tr'):
            row_text = []
            for td in tr.find_all(['td', 'th']):
                cell_text = td.get_text(strip=True)
                row_text.append(cell_text)
            if row_text:
                rows.append(' | '.join(row_text))
        
        if rows:
            return {
                'type': 'table',
                'text': '\n'.join(rows)
            }
        return None
    
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
                return {'type': 'text', 'text': self._sanitize_text_content(text)}
        
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
            'text': self._sanitize_text_content(element.get_text(strip=True))
        }
    
    def _convert_list(self, element) -> Dict[str, Any]:
        """Convert list element"""
        items = []
        for li in element.find_all('li', recursive=False):
            items.append(self._sanitize_text_content(li.get_text(strip=True)))
        
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
            'text': self._sanitize_text_content(element.get_text(strip=True))
        }
    
    def _extract_formatted_text(self, element) -> str:
        """Extract text with inline formatting preserved"""
        # KISS: Just get text for now, handle formatting in Phase 4
        text = element.get_text(strip=True)
        
        # Sanitize text for ReportLab compatibility
        return self._sanitize_text_content(text)
    
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
    
    def _is_code_element(self, element_tag: str, element_classes: list = None, styles: dict = None) -> bool:
        """Detect if an element should be treated as code"""
        element_classes = element_classes or []
        styles = styles or {}
        
        # Check tag names
        if element_tag in ['code', 'pre', 'samp', 'kbd', 'var']:
            return True
        
        # Check common code classes
        code_class_patterns = [
            'code', 'highlight', 'codehilite', 'sourceCode', 'language-',
            'hljs', 'prettyprint', 'syntax', 'brush:', 'programlisting'
        ]
        
        for class_name in element_classes:
            for pattern in code_class_patterns:
                if pattern in class_name.lower():
                    return True
        
        # Check CSS styles that indicate code
        font_family = styles.get('font-family', '').lower()
        if any(font in font_family for font in ['monospace', 'courier', 'console', 'source code pro']):
            return True
        
        if styles.get('white-space') in ['pre', 'pre-wrap', 'pre-line']:
            return True
        
        return False

    def _extract_code_text(self, element) -> str:
        """Extract code text while preserving formatting"""
        # Use get_text with specific separators to preserve structure
        text = element.get_text(separator='\n', strip=False)
        
        # Only clean up problematic characters, preserve whitespace structure
        text = text.replace('\xa0', ' ')  # Non-breaking space
        text = text.replace('\u2060', '')  # Word joiner
        text = text.replace('\u200b', '')  # Zero-width space
        
        # Don't strip leading/trailing whitespace for code blocks
        return text

    def _detect_code_language(self, classes: list) -> str:
        """Detect programming language from CSS classes"""
        for class_name in classes:
            class_lower = class_name.lower()
            if class_lower.startswith('language-'):
                return class_lower[9:]  # Remove 'language-' prefix
            elif class_lower.startswith('lang-'):
                return class_lower[5:]   # Remove 'lang-' prefix
            elif class_lower.startswith('brush:'):
                return class_lower[6:]   # Remove 'brush:' prefix
        
        return 'text'  # Default to plain text

    def _parse_style_string(self, style_str: str) -> dict:
        """Parse CSS style string into dictionary"""
        styles = {}
        if not style_str:
            return styles
            
        for declaration in style_str.split(';'):
            if ':' in declaration:
                prop, value = declaration.split(':', 1)
                styles[prop.strip()] = value.strip()
        
        return styles

    def _deduplicate_elements(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate elements based on content similarity"""
        deduplicated = []
        seen_headings = set()  # Track heading text separately
        seen_content = set()   # Track other content
        
        for element in elements:
            element_type = element.get('type', '')
            text_content = element.get('text', '').strip()
            
            # Always include images, breaks, and non-text elements
            if element_type in ['image', 'break'] or not text_content:
                deduplicated.append(element)
                continue
            
            # Special handling for headings - more strict deduplication
            if element_type == 'heading':
                # For headings, check exact text match (case-insensitive)
                heading_key = (text_content.lower(), element.get('level', 1))
                if heading_key not in seen_headings:
                    seen_headings.add(heading_key)
                    deduplicated.append(element)
                # Skip duplicate headings completely
            else:
                # For other content, use existing logic but be less aggressive
                if len(text_content) > 30:  # Only deduplicate longer content
                    content_hash = hash(text_content[:150])  # Use first 150 chars
                    
                    if content_hash not in seen_content:
                        seen_content.add(content_hash)
                        deduplicated.append(element)
                else:
                    # For short content, always include
                    deduplicated.append(element)
        
        return deduplicated

    def _sanitize_text_content(self, text: str) -> str:
        """Sanitize text content to prevent ReportLab parsing issues"""
        if not text:
            return text
        
        # Replace problematic Unicode characters
        text = text.replace('\xa0', ' ')  # Non-breaking space
        text = text.replace('\u2060', '')  # Word joiner
        text = text.replace('\u200b', '')  # Zero-width space
        text = text.replace('\u2003', ' ')  # Em space
        text = text.replace('\u2002', ' ')  # En space
        text = text.replace('\u2009', ' ')  # Thin space
        
        # Remove or escape any remaining HTML-like content
        text = re.sub(r'<[^>]*>', '', text)  # Remove any HTML tags
        
        # Escape characters that might confuse ReportLab's paragraph parser
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('&', '&amp;')
        
        # Clean up excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text