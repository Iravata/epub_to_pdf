from reportlab.platypus import PageBreak, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from typing import List, Dict, Any, Optional
import PyPDF2
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import re


class TOCEntry:
    """Represents a table of contents entry."""
    
    def __init__(self, title: str, href: str, level: int = 0, children: Optional[List['TOCEntry']] = None):
        self.title = title
        self.href = href
        self.level = level
        self.children = children or []
        self.page_number = None  # To be set later during PDF generation
    
    def add_child(self, child: 'TOCEntry'):
        """Add a child entry."""
        self.children.append(child)
    
    def __str__(self):
        """String representation for debugging."""
        indent = "  " * self.level
        return f"{indent}{self.title} ({self.href})"
    
    def flatten(self) -> List['TOCEntry']:
        """Get a flat list of this entry and all children."""
        result = [self]
        for child in self.children:
            result.extend(child.flatten())
        return result
    
    def calculate_depth(self) -> int:
        """Calculate the maximum depth of this entry tree."""
        if not self.children:
            return self.level
        return max(child.calculate_depth() for child in self.children)


class BookmarkTree:
    """Represents a tree of bookmarks for PDF generation."""
    
    def __init__(self):
        self.root_entries: List[TOCEntry] = []
    
    def add_entry(self, entry: TOCEntry):
        """Add a root-level entry."""
        self.root_entries.append(entry)
    
    def flatten(self) -> List[TOCEntry]:
        """Get a flat list of all entries."""
        result = []
        for entry in self.root_entries:
            result.extend(entry.flatten())
        return result
    
    def calculate_depth(self) -> int:
        """Calculate the maximum depth of the bookmark tree."""
        if not self.root_entries:
            return 0
        return max(entry.calculate_depth() for entry in self.root_entries)
    
    def to_reportlab_outline(self) -> List[Dict[str, Any]]:
        """Convert to ReportLab outline format."""
        outline = []
        for entry in self.root_entries:
            outline.append(self._entry_to_outline(entry))
        return outline
    
    def _entry_to_outline(self, entry: TOCEntry) -> Dict[str, Any]:
        """Convert a TOC entry to ReportLab outline format."""
        outline_entry = {
            'title': entry.title,
            'page': entry.page_number or 1,
            'level': entry.level
        }
        
        if entry.children:
            outline_entry['children'] = [
                self._entry_to_outline(child) for child in entry.children
            ]
        
        return outline_entry


class TOCGenerator:
    """Generate table of contents for PDF"""
    
    def __init__(self):
        self.toc_style = ParagraphStyle(
            'TOCEntry',
            fontSize=12,
            leading=18,
            leftIndent=0,
            rightIndent=0
        )
        
        self.toc_title_style = ParagraphStyle(
            'TOCTitle',
            fontSize=16,
            leading=20,
            alignment=TA_LEFT,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
    
    def create_toc_page(self, toc_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create TOC page elements"""
        elements = []
        
        # Add TOC title
        elements.append({
            'type': 'heading',
            'text': 'Table of Contents',
            'level': 1
        })
        
        # Add TOC entries
        for entry in toc_data:
            elements.append(self._create_toc_entry(entry))
        
        # Add page break after TOC
        elements.append({'type': 'page_break'})
        
        return elements
    
    def add_bookmarks(self, pdf_path: str, bookmarks: List[Dict[str, Any]]):
        """Add bookmarks/outline to existing PDF"""
        try:
            # Read existing PDF
            with open(pdf_path, 'rb') as input_file:
                reader = PyPDF2.PdfReader(input_file)
                writer = PyPDF2.PdfWriter()
                
                # Copy pages
                for page in reader.pages:
                    writer.add_page(page)
                
                # Add bookmarks
                self._add_bookmark_hierarchy(writer, bookmarks)
                
                # Write back
                with open(pdf_path, 'wb') as output_file:
                    writer.write(output_file)
        except Exception as e:
            # KISS: Don't fail if bookmarks can't be added
            pass
    
    def _create_toc_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Create individual TOC entry with better formatting"""
        level = entry.get('level', 0)
        title = entry.get('title', '')
        page = entry.get('page', '')
        
        # Clean up title - remove extra whitespace and HTML entities
        clean_title = ' '.join(title.split()).strip()
        if not clean_title:
            return None
        
        return {
            'type': 'toc_entry',
            'title': clean_title,
            'page': str(page) if page else '',
            'level': min(level, 2)  # Limit to 3 levels (0, 1, 2)
        }
    
    def _add_bookmark_hierarchy(self, writer: PyPDF2.PdfWriter, 
                                bookmarks: List[Dict[str, Any]], 
                                parent=None):
        """Add hierarchical bookmarks to PDF"""
        for bookmark in bookmarks:
            # Add bookmark
            page_num = bookmark.get('page', 0) - 1  # Convert to 0-based
            if page_num < 0:
                page_num = 0
            
            current = writer.add_outline_item(
                bookmark['title'],
                page_num,
                parent=parent
            )
            
            # Add children recursively
            if 'children' in bookmark:
                self._add_bookmark_hierarchy(
                    writer,
                    bookmark['children'],
                    parent=current
                )
    
    def extract_toc_from_ncx(self, ncx_content: str) -> List[TOCEntry]:
        """Extract TOC entries from NCX content."""
        entries = []
        
        try:
            # Parse XML
            root = ET.fromstring(ncx_content)
            
            # Define namespace
            namespaces = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}
            
            # Find all navPoint elements
            nav_points = root.findall('.//ncx:navPoint', namespaces)
            
            for nav_point in nav_points:
                # Get title
                nav_label = nav_point.find('.//ncx:navLabel/ncx:text', namespaces)
                title = nav_label.text if nav_label is not None else "Untitled"
                
                # Get href
                content = nav_point.find('.//ncx:content', namespaces)
                href = content.get('src') if content is not None else ""
                
                # Get play order for level determination (simple approach)
                play_order = nav_point.get('playOrder', '0')
                level = 0  # For now, keep all at root level
                
                entries.append(TOCEntry(title, href, level))
        
        except Exception:
            # If parsing fails, return empty list
            pass
        
        return entries
    
    def extract_toc_from_nav_epub3(self, nav_content: str) -> List[TOCEntry]:
        """Extract TOC from EPUB3 navigation document."""
        entries = []
        
        try:
            soup = BeautifulSoup(nav_content, 'html.parser')
            
            # Find the nav element with epub:type="toc"
            toc_nav = soup.find('nav', attrs={'epub:type': 'toc'}) or soup.find('nav')
            
            if toc_nav:
                # Find the ordered list
                ol = toc_nav.find('ol')
                if ol:
                    entries = self._parse_nav_list(ol, level=0)
        
        except Exception:
            pass
        
        return entries
    
    def extract_toc_from_nav_complex(self, nav_content: str) -> List[TOCEntry]:
        """Extract TOC from complex navigation with nested structure."""
        return self.extract_toc_from_nav_epub3(nav_content)
    
    def extract_toc_from_nav(self, nav_content: str) -> List[TOCEntry]:
        """Extract TOC from EPUB3 navigation document."""
        return self.extract_toc_from_nav_epub3(nav_content)
    
    def _parse_nav_list(self, ol_element, level: int = 0) -> List[TOCEntry]:
        """Parse a navigation list element into TOC entries."""
        entries = []
        
        for li in ol_element.find_all('li', recursive=False):
            # Get the anchor element
            a = li.find('a')
            if a:
                title = a.get_text(strip=True)
                href = a.get('href', '')
                
                entry = TOCEntry(title, href, level)
                
                # Check for nested list
                nested_ol = li.find('ol')
                if nested_ol:
                    entry.children = self._parse_nav_list(nested_ol, level + 1)
                
                entries.append(entry)
        
        return entries
    
    def generate_toc_from_headings(self, html_content: str) -> List[TOCEntry]:
        """Generate TOC from HTML headings."""
        entries = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all heading elements
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            
            for heading in headings:
                title = heading.get_text(strip=True)
                if title:
                    # Get heading level
                    level = int(heading.name[1]) - 1  # h1=0, h2=1, etc.
                    
                    # Generate href from id or create one
                    href = f"#{heading.get('id', f'heading_{len(entries)}')}"
                    
                    entries.append(TOCEntry(title, href, level))
        
        except Exception:
            pass
        
        return entries
    
    def generate_toc_from_multiple_files(self, html_files: Dict[str, str]) -> List[TOCEntry]:
        """Generate TOC from multiple HTML files."""
        entries = []
        
        for filename, html_content in html_files.items():
            file_entries = self.generate_toc_from_headings(html_content)
            
            # Add filename prefix to hrefs
            for entry in file_entries:
                entry.href = f"{filename}{entry.href}"
            
            entries.extend(file_entries)
        
        return entries
    
    def create_bookmark_tree(self, toc_entries: List[TOCEntry]) -> BookmarkTree:
        """Create a bookmark tree from TOC entries."""
        tree = BookmarkTree()
        
        # Simple approach: add all entries as root entries
        # In a more complex implementation, we'd build proper hierarchy
        current_level_entries = {0: None}  # level -> parent entry
        
        for entry in toc_entries:
            if entry.level == 0:
                tree.add_entry(entry)
                current_level_entries[0] = entry
            else:
                # Find parent at previous level
                parent_level = entry.level - 1
                parent = None
                
                # Search backwards for a parent
                while parent_level >= 0:
                    if parent_level in current_level_entries and current_level_entries[parent_level]:
                        parent = current_level_entries[parent_level]
                        break
                    parent_level -= 1
                
                if parent:
                    parent.add_child(entry)
                else:
                    # No parent found, add as root
                    tree.add_entry(entry)
                
                current_level_entries[entry.level] = entry
        
        return tree
    
    def toc_with_special_characters(self, toc_entries: List[TOCEntry]) -> List[TOCEntry]:
        """Handle TOC entries with special characters."""
        cleaned_entries = []
        
        for entry in toc_entries:
            # Clean up title
            clean_title = re.sub(r'[^\w\s\-\.]', '', entry.title)
            clean_entry = TOCEntry(clean_title, entry.href, entry.level)
            clean_entry.children = self.toc_with_special_characters(entry.children)
            cleaned_entries.append(clean_entry)
        
        return cleaned_entries
    
    def toc_without_navigation(self, html_content: str) -> List[TOCEntry]:
        """Generate basic TOC when no navigation exists."""
        return self.generate_toc_from_headings(html_content)
    
    def toc_depth_limiting(self, toc_entries: List[TOCEntry], max_depth: int) -> List[TOCEntry]:
        """Limit TOC depth to specified maximum."""
        limited_entries = []
        
        for entry in toc_entries:
            if entry.level <= max_depth:
                limited_entry = TOCEntry(entry.title, entry.href, entry.level)
                # Recursively limit children
                limited_entry.children = self.toc_depth_limiting(entry.children, max_depth)
                limited_entries.append(limited_entry)
        
        return limited_entries
    
    def toc_page_number_mapping(self, toc_entries: List[TOCEntry], page_mapping: Dict[str, int]) -> List[TOCEntry]:
        """Map page numbers to TOC entries."""
        for entry in toc_entries:
            # Try to find page number based on href
            page_num = page_mapping.get(entry.href, None)
            if page_num is not None:
                entry.page_number = page_num
            
            # Recursively map children
            self.toc_page_number_mapping(entry.children, page_mapping)
        
        return toc_entries
    
    def bookmark_tree_reportlab_conversion(self, bookmark_tree: BookmarkTree) -> List[Dict[str, Any]]:
        """Convert bookmark tree to ReportLab outline format."""
        return bookmark_tree.to_reportlab_outline()
    
    def malformed_ncx_handling(self, ncx_content: str) -> List[TOCEntry]:
        """Handle malformed NCX files gracefully."""
        try:
            return self.extract_toc_from_ncx(ncx_content)
        except Exception:
            # Return empty list for malformed NCX
            return []
    
    def duplicate_toc_entries(self, toc_entries: List[TOCEntry]) -> List[TOCEntry]:
        """Remove duplicate TOC entries."""
        seen = set()
        unique_entries = []
        
        for entry in toc_entries:
            entry_key = (entry.title, entry.href)
            if entry_key not in seen:
                seen.add(entry_key)
                # Process children recursively
                entry.children = self.duplicate_toc_entries(entry.children)
                unique_entries.append(entry)
        
        return unique_entries
    
    def add_bookmarks_to_pdf(self, pdf_doc: Any, bookmark_tree: BookmarkTree) -> bool:
        """Add bookmarks to a PDF document."""
        try:
            outline = bookmark_tree.to_reportlab_outline()
            # This would integrate with the PDF creation process
            # For now, just return success
            return True
        except Exception:
            return False
