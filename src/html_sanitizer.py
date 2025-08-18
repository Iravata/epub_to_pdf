"""HTML sanitization module for handling malformed EPUB content"""

import re
from bs4 import BeautifulSoup
from typing import Dict, List, Set


class HTMLSanitizer:
    """Sanitize and fix malformed HTML content from EPUBs"""
    
    def __init__(self):
        # Known problematic tags that need fixing
        self.problematic_tags = {
            'para': 'p',  # Convert <para> to <p>
            'emphasis': 'em',
            'strong': 'strong',
            'code': 'code'
        }
        
        # Self-closing tags that don't need closing
        self.self_closing_tags = {
            'br', 'hr', 'img', 'input', 'meta', 'link', 'area', 'base', 'col',
            'embed', 'source', 'track', 'wbr'
        }
    
    def sanitize(self, html_content: str) -> str:
        """Sanitize HTML content to fix common issues"""
        if not html_content or not html_content.strip():
            return html_content
        
        # Step 1: Fix known problematic tags
        html_content = self._fix_problematic_tags(html_content)
        
        # Step 2: Fix unclosed tags
        html_content = self._fix_unclosed_tags(html_content)
        
        # Step 3: Remove or escape problematic content
        html_content = self._remove_problematic_content(html_content)
        
        # Step 4: Validate with BeautifulSoup and fix
        html_content = self._validate_and_fix(html_content)
        
        return html_content
    
    def _fix_problematic_tags(self, html: str) -> str:
        """Fix known problematic tags like <para> -> <p>"""
        for old_tag, new_tag in self.problematic_tags.items():
            # Replace opening tags
            html = re.sub(
                rf'<{old_tag}(\s[^>]*)?>', 
                rf'<{new_tag}\1>', 
                html, 
                flags=re.IGNORECASE
            )
            # Replace closing tags
            html = re.sub(
                rf'</{old_tag}>', 
                f'</{new_tag}>', 
                html, 
                flags=re.IGNORECASE
            )
        
        return html
    
    def _fix_unclosed_tags(self, html: str) -> str:
        """Find and fix unclosed tags"""
        # Find all opening tags
        opening_tags = re.findall(r'<([a-zA-Z][a-zA-Z0-9]*)[^>]*?>', html)
        
        # Find all closing tags
        closing_tags = re.findall(r'</([a-zA-Z][a-zA-Z0-9]*?)>', html)
        
        # Convert to sets for comparison (case insensitive)
        opening_set = {tag.lower() for tag in opening_tags if tag.lower() not in self.self_closing_tags}
        closing_set = {tag.lower() for tag in closing_tags}
        
        # Find unclosed tags
        unclosed_tags = opening_set - closing_set
        
        # Add closing tags at the end
        for tag in unclosed_tags:
            html += f'</{tag}>'
        
        return html
    
    def _remove_problematic_content(self, html: str) -> str:
        """Remove or escape content that might cause parsing issues"""
        # Remove XML processing instructions
        html = re.sub(r'<\?xml[^>]*\?>', '', html)
        
        # Remove DOCTYPE declarations
        html = re.sub(r'<!DOCTYPE[^>]*>', '', html)
        
        # Fix malformed attributes (remove quotes around attribute names)
        html = re.sub(r'="([^"]*)"=', r'="\1"', html)
        
        # Remove empty attributes
        html = re.sub(r'\s+\w+=""', '', html)
        
        return html
    
    def _validate_and_fix(self, html: str) -> str:
        """Use BeautifulSoup to validate and fix remaining issues"""
        try:
            # Parse with BeautifulSoup (lenient parser)
            soup = BeautifulSoup(html, 'html.parser')
            
            # Convert back to string (this fixes many issues automatically)
            return str(soup)
            
        except Exception:
            # If BeautifulSoup fails, return cleaned text content only
            return self._extract_safe_text(html)
    
    def _extract_safe_text(self, html: str) -> str:
        """Extract only text content as a fallback"""
        # Remove all HTML tags
        text = re.sub(r'<[^>]+>', '', html)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Wrap in a simple paragraph
        return f'<p>{text}</p>' if text else ''
    
    def get_sanitization_report(self, original: str, sanitized: str) -> Dict[str, any]:
        """Generate a report of what was sanitized"""
        report = {
            'original_length': len(original),
            'sanitized_length': len(sanitized),
            'tags_fixed': [],
            'issues_found': []
        }
        
        # Check for problematic tags that were fixed
        for old_tag in self.problematic_tags.keys():
            if f'<{old_tag}' in original.lower():
                report['tags_fixed'].append(old_tag)
        
        # Check for unclosed tags
        opening_tags = len(re.findall(r'<[a-zA-Z][^>]*?>', original))
        closing_tags = len(re.findall(r'</[a-zA-Z][^>]*?>', original))
        
        if opening_tags != closing_tags:
            report['issues_found'].append(f'Unclosed tags: {opening_tags - closing_tags}')
        
        return report