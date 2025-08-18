"""Tests for TOC generation and PDF bookmarks."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile

# Import the TOC generator that needs to be implemented
# These imports will initially fail but define the expected interface
try:
    from src.toc_generator import TOCGenerator, TOCEntry, BookmarkTree
except ImportError:
    # Define mock classes for TDD - these represent the expected interface
    class TOCEntry:
        def __init__(self, title, href, level=0, children=None):
            self.title = title
            self.href = href
            self.level = level
            self.children = children or []
        
        def add_child(self, child):
            self.children.append(child)
    
    class BookmarkTree:
        def __init__(self):
            self.root_entries = []
        
        def add_entry(self, entry):
            self.root_entries.append(entry)
        
        def to_reportlab_outline(self):
            pass
    
    class TOCGenerator:
        def __init__(self):
            pass
        
        def extract_toc_from_ncx(self, ncx_content):
            pass
        
        def extract_toc_from_nav(self, nav_content):
            pass
        
        def generate_toc_from_headings(self, html_content):
            pass
        
        def create_bookmark_tree(self, toc_entries):
            pass
        
        def add_bookmarks_to_pdf(self, pdf_doc, bookmark_tree):
            pass


class TestTOCGenerator:
    """Test suite for TOC generation functionality."""
    
    def test_toc_generator_initialization(self):
        """Test TOC generator can be initialized properly."""
        generator = TOCGenerator()
        assert generator is not None
    
    def test_extract_toc_from_ncx_basic(self):
        """Test extracting TOC from NCX file with basic structure."""
        generator = TOCGenerator()
        
        ncx_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
            <head>
                <meta name="dtb:uid" content="123"/>
            </head>
            <docTitle>
                <text>Test Book</text>
            </docTitle>
            <navMap>
                <navPoint id="navpoint1" playOrder="1">
                    <navLabel>
                        <text>Chapter 1</text>
                    </navLabel>
                    <content src="chapter1.html"/>
                </navPoint>
                <navPoint id="navpoint2" playOrder="2">
                    <navLabel>
                        <text>Chapter 2</text>
                    </navLabel>
                    <content src="chapter2.html"/>
                </navPoint>
            </navMap>
        </ncx>'''
        
        toc_entries = generator.extract_toc_from_ncx(ncx_content)
        
        assert isinstance(toc_entries, list)
        assert len(toc_entries) == 2
        
        # Check first entry
        assert toc_entries[0].title == "Chapter 1"
        assert toc_entries[0].href == "chapter1.html"
        assert toc_entries[0].level == 0
        
        # Check second entry
        assert toc_entries[1].title == "Chapter 2"
        assert toc_entries[1].href == "chapter2.html"
        assert toc_entries[1].level == 0
    
    def test_extract_toc_from_ncx_nested(self, nested_toc_epub):
        """Test extracting nested TOC structure from NCX."""
        generator = TOCGenerator()
        
        # Read NCX content from nested EPUB
        import zipfile
        with zipfile.ZipFile(nested_toc_epub, 'r') as epub:
            ncx_content = epub.read('toc.ncx').decode('utf-8')
        
        toc_entries = generator.extract_toc_from_ncx(ncx_content)
        
        assert isinstance(toc_entries, list)
        assert len(toc_entries) >= 1
        
        # Should have nested structure
        main_chapter = toc_entries[0]
        assert main_chapter.title == "Chapter 1"
        assert len(main_chapter.children) >= 1
        
        # Check nested entry
        nested_section = main_chapter.children[0]
        assert nested_section.title == "Section 1.1"
        assert nested_section.level == 1
    
    def test_extract_toc_from_nav_epub3(self, epub3_with_nav):
        """Test extracting TOC from EPUB3 nav document."""
        generator = TOCGenerator()
        
        # Read nav content from EPUB3
        import zipfile
        with zipfile.ZipFile(epub3_with_nav, 'r') as epub:
            nav_content = epub.read('nav.xhtml').decode('utf-8')
        
        toc_entries = generator.extract_toc_from_nav(nav_content)
        
        assert isinstance(toc_entries, list)
        assert len(toc_entries) >= 1
        
        entry = toc_entries[0]
        assert entry.title == "Chapter 1"
        assert entry.href == "chapter1.html"
    
    def test_extract_toc_from_nav_complex(self):
        """Test extracting TOC from complex EPUB3 nav structure."""
        generator = TOCGenerator()
        
        nav_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
            <head>
                <title>Navigation</title>
            </head>
            <body>
                <nav epub:type="toc">
                    <h1>Contents</h1>
                    <ol>
                        <li><a href="part1.html">Part I: Introduction</a>
                            <ol>
                                <li><a href="chapter1.html">Chapter 1: Overview</a></li>
                                <li><a href="chapter2.html">Chapter 2: History</a></li>
                            </ol>
                        </li>
                        <li><a href="part2.html">Part II: Details</a>
                            <ol>
                                <li><a href="chapter3.html">Chapter 3: Technical</a></li>
                            </ol>
                        </li>
                    </ol>
                </nav>
            </body>
        </html>'''
        
        toc_entries = generator.extract_toc_from_nav(nav_content)
        
        assert isinstance(toc_entries, list)
        assert len(toc_entries) == 2  # Two main parts
        
        # Check first part structure
        part1 = toc_entries[0]
        assert part1.title == "Part I: Introduction"
        assert part1.href == "part1.html"
        assert len(part1.children) == 2
        
        # Check nested chapters
        chapter1 = part1.children[0]
        assert chapter1.title == "Chapter 1: Overview"
        assert chapter1.level == 1
    
    def test_generate_toc_from_headings(self):
        """Test generating TOC from HTML headings when no nav exists."""
        generator = TOCGenerator()
        
        html_content = '''
        <html>
            <body>
                <h1 id="ch1">Chapter 1: Introduction</h1>
                <p>Some content...</p>
                <h2 id="sec1-1">1.1 Overview</h2>
                <p>More content...</p>
                <h2 id="sec1-2">1.2 Background</h2>
                <p>Content...</p>
                <h1 id="ch2">Chapter 2: Details</h1>
                <p>Content...</p>
                <h3 id="sec2-1-1">2.1.1 Subsection</h3>
            </body>
        </html>
        '''
        
        toc_entries = generator.generate_toc_from_headings(html_content)
        
        assert isinstance(toc_entries, list)
        assert len(toc_entries) >= 2  # At least 2 h1 elements
        
        # Check first chapter
        ch1 = toc_entries[0]
        assert "Chapter 1" in ch1.title
        assert ch1.href == "#ch1"
        assert ch1.level == 0
        
        # Should have h2 children
        assert len(ch1.children) >= 2
        sec1_1 = ch1.children[0]
        assert "1.1" in sec1_1.title
        assert sec1_1.level == 1
    
    def test_generate_toc_from_multiple_files(self):
        """Test generating TOC from multiple HTML files."""
        generator = TOCGenerator()
        
        html_files = {
            "chapter1.html": "<html><body><h1>Chapter 1</h1><h2>Section 1.1</h2></body></html>",
            "chapter2.html": "<html><body><h1>Chapter 2</h1><h2>Section 2.1</h2></body></html>"
        }
        
        toc_entries = generator.generate_toc_from_files(html_files)
        
        assert isinstance(toc_entries, list)
        assert len(toc_entries) >= 2
        
        # Entries should include file references
        ch1 = next((e for e in toc_entries if "Chapter 1" in e.title), None)
        assert ch1 is not None
        assert "chapter1.html" in ch1.href
    
    def test_create_bookmark_tree(self):
        """Test creating bookmark tree from TOC entries."""
        generator = TOCGenerator()
        
        toc_entries = [
            TOCEntry("Chapter 1", "ch1.html", 0, [
                TOCEntry("Section 1.1", "ch1.html#sec1", 1),
                TOCEntry("Section 1.2", "ch1.html#sec2", 1)
            ]),
            TOCEntry("Chapter 2", "ch2.html", 0)
        ]
        
        bookmark_tree = generator.create_bookmark_tree(toc_entries)
        
        assert isinstance(bookmark_tree, BookmarkTree)
        assert len(bookmark_tree.root_entries) == 2
        
        # Check structure preservation
        ch1_bookmark = bookmark_tree.root_entries[0]
        assert ch1_bookmark.title == "Chapter 1"
        assert len(ch1_bookmark.children) == 2
    
    def test_add_bookmarks_to_pdf(self):
        """Test adding bookmarks to PDF document."""
        generator = TOCGenerator()
        
        # Mock PDF document
        mock_pdf = Mock()
        mock_canvas = Mock()
        mock_pdf.canv = mock_canvas
        
        bookmark_tree = BookmarkTree()
        bookmark_tree.add_entry(TOCEntry("Chapter 1", "#page1", 0))
        bookmark_tree.add_entry(TOCEntry("Chapter 2", "#page5", 0))
        
        # Should not raise exception
        generator.add_bookmarks_to_pdf(mock_pdf, bookmark_tree)
        
        # Should have called bookmark methods on PDF
        # This will be implemented when the actual PDF library integration is done
    
    def test_toc_with_special_characters(self):
        """Test TOC extraction with special characters and encoding."""
        generator = TOCGenerator()
        
        ncx_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
            <navMap>
                <navPoint id="navpoint1" playOrder="1">
                    <navLabel>
                        <text>Chapitre 1: Café &amp; Thé</text>
                    </navLabel>
                    <content src="chapter1.html"/>
                </navPoint>
                <navPoint id="navpoint2" playOrder="2">
                    <navLabel>
                        <text>Chapter 2: "Quotes" &amp; 'Apostrophes'</text>
                    </navLabel>
                    <content src="chapter2.html"/>
                </navPoint>
            </navMap>
        </ncx>'''
        
        toc_entries = generator.extract_toc_from_ncx(ncx_content)
        
        assert len(toc_entries) == 2
        
        # Should handle Unicode characters
        assert "Café" in toc_entries[0].title
        
        # Should handle HTML entities
        assert "&" in toc_entries[0].title or "Thé" in toc_entries[0].title
        assert '"' in toc_entries[1].title or "Quotes" in toc_entries[1].title
    
    def test_toc_without_navigation(self, epub_without_toc):
        """Test fallback TOC generation when no navigation exists."""
        generator = TOCGenerator()
        
        # Extract HTML content from EPUB without TOC
        import zipfile
        html_contents = {}
        with zipfile.ZipFile(epub_without_toc, 'r') as epub:
            for file_info in epub.filelist:
                if file_info.filename.endswith('.html'):
                    html_contents[file_info.filename] = epub.read(file_info.filename).decode('utf-8')
        
        toc_entries = generator.generate_fallback_toc(html_contents)
        
        assert isinstance(toc_entries, list)
        assert len(toc_entries) >= 1  # Should find at least chapter headings
        
        # Should create entries based on file structure
        for entry in toc_entries:
            assert entry.title is not None
            assert entry.href is not None
    
    def test_toc_depth_limiting(self):
        """Test limiting TOC depth for cleaner PDF bookmarks."""
        generator = TOCGenerator()
        
        html_content = '''
        <html><body>
            <h1>Chapter 1</h1>
            <h2>Section 1.1</h2>
            <h3>Subsection 1.1.1</h3>
            <h4>Sub-subsection 1.1.1.1</h4>
            <h5>Deep heading</h5>
            <h6>Very deep heading</h6>
        </body></html>
        '''
        
        # Test with depth limit
        toc_entries = generator.generate_toc_from_headings(html_content, max_depth=2)
        
        assert len(toc_entries) >= 1
        
        # Should only go 2 levels deep
        ch1 = toc_entries[0]
        assert len(ch1.children) >= 1  # h2 should be included
        
        sec1_1 = ch1.children[0]
        if len(sec1_1.children) > 0:
            # h3 might be included depending on implementation
            # h4, h5, h6 should not be at deep levels
            max_level = max(child.level for child in sec1_1.children)
            assert max_level <= 2
    
    def test_toc_page_number_mapping(self):
        """Test mapping TOC entries to PDF page numbers."""
        generator = TOCGenerator()
        
        toc_entries = [
            TOCEntry("Chapter 1", "chapter1.html", 0),
            TOCEntry("Chapter 2", "chapter2.html", 0),
            TOCEntry("Chapter 3", "chapter3.html", 0)
        ]
        
        # Mock page mapping
        page_mapping = {
            "chapter1.html": 1,
            "chapter2.html": 15,
            "chapter3.html": 30
        }
        
        updated_entries = generator.map_to_page_numbers(toc_entries, page_mapping)
        
        assert len(updated_entries) == 3
        assert updated_entries[0].page_number == 1
        assert updated_entries[1].page_number == 15
        assert updated_entries[2].page_number == 30
    
    def test_bookmark_tree_reportlab_conversion(self):
        """Test converting bookmark tree to ReportLab outline format."""
        bookmark_tree = BookmarkTree()
        
        # Create nested structure
        ch1 = TOCEntry("Chapter 1", "#page1", 0)
        ch1.add_child(TOCEntry("Section 1.1", "#page2", 1))
        ch1.add_child(TOCEntry("Section 1.2", "#page5", 1))
        
        bookmark_tree.add_entry(ch1)
        bookmark_tree.add_entry(TOCEntry("Chapter 2", "#page10", 0))
        
        outline = bookmark_tree.to_reportlab_outline()
        
        # Should convert to ReportLab-compatible format
        assert isinstance(outline, list)
        assert len(outline) >= 2
        
        # Check structure preservation
        ch1_outline = outline[0]
        assert "Chapter 1" in str(ch1_outline)
        # Should have nested items for sections
    
    def test_malformed_ncx_handling(self):
        """Test handling malformed or invalid NCX content."""
        generator = TOCGenerator()
        
        # Test various malformed NCX scenarios
        malformed_cases = [
            "<invalid>xml</invalid>",  # Invalid XML
            "<?xml version='1.0'?><ncx></ncx>",  # Empty NCX
            "not xml at all",  # Not XML
            ""  # Empty content
        ]
        
        for malformed_ncx in malformed_cases:
            toc_entries = generator.extract_toc_from_ncx(malformed_ncx)
            
            # Should not crash, return empty list or minimal structure
            assert isinstance(toc_entries, list)
    
    def test_duplicate_toc_entries(self):
        """Test handling duplicate TOC entries."""
        generator = TOCGenerator()
        
        toc_entries = [
            TOCEntry("Chapter 1", "chapter1.html", 0),
            TOCEntry("Chapter 1", "chapter1.html", 0),  # Duplicate
            TOCEntry("Chapter 2", "chapter2.html", 0)
        ]
        
        cleaned_entries = generator.remove_duplicates(toc_entries)
        
        assert len(cleaned_entries) == 2
        titles = [entry.title for entry in cleaned_entries]
        assert titles.count("Chapter 1") == 1


class TestTOCEntry:
    """Test suite for TOC Entry functionality."""
    
    def test_toc_entry_creation(self):
        """Test creating TOC entry objects."""
        entry = TOCEntry("Chapter 1", "chapter1.html", 0)
        
        assert entry.title == "Chapter 1"
        assert entry.href == "chapter1.html"
        assert entry.level == 0
        assert len(entry.children) == 0
    
    def test_toc_entry_add_child(self):
        """Test adding child entries to TOC entry."""
        parent = TOCEntry("Chapter 1", "chapter1.html", 0)
        child = TOCEntry("Section 1.1", "chapter1.html#sec1", 1)
        
        parent.add_child(child)
        
        assert len(parent.children) == 1
        assert parent.children[0] == child
        assert parent.children[0].level == 1
    
    def test_toc_entry_hierarchy(self):
        """Test TOC entry hierarchy management."""
        root = TOCEntry("Root", "index.html", 0)
        ch1 = TOCEntry("Chapter 1", "ch1.html", 1)
        sec1_1 = TOCEntry("Section 1.1", "ch1.html#s1", 2)
        sec1_2 = TOCEntry("Section 1.2", "ch1.html#s2", 2)
        
        ch1.add_child(sec1_1)
        ch1.add_child(sec1_2)
        root.add_child(ch1)
        
        # Test hierarchy
        assert len(root.children) == 1
        assert len(root.children[0].children) == 2
        
        # Test level consistency
        assert root.level == 0
        assert root.children[0].level == 1
        assert root.children[0].children[0].level == 2
    
    def test_toc_entry_string_representation(self):
        """Test string representation of TOC entries."""
        entry = TOCEntry("Chapter 1: Introduction", "chapter1.html", 0)
        
        str_repr = str(entry)
        
        # Should contain useful information
        assert "Chapter 1" in str_repr
        assert "Introduction" in str_repr or "chapter1.html" in str_repr


class TestBookmarkTree:
    """Test suite for Bookmark Tree functionality."""
    
    def test_bookmark_tree_creation(self):
        """Test creating bookmark tree objects."""
        tree = BookmarkTree()
        
        assert isinstance(tree.root_entries, list)
        assert len(tree.root_entries) == 0
    
    def test_bookmark_tree_add_entry(self):
        """Test adding entries to bookmark tree."""
        tree = BookmarkTree()
        entry = TOCEntry("Chapter 1", "ch1.html", 0)
        
        tree.add_entry(entry)
        
        assert len(tree.root_entries) == 1
        assert tree.root_entries[0] == entry
    
    def test_bookmark_tree_flatten(self):
        """Test flattening bookmark tree for simple navigation."""
        tree = BookmarkTree()
        
        ch1 = TOCEntry("Chapter 1", "ch1.html", 0)
        ch1.add_child(TOCEntry("Section 1.1", "ch1.html#s1", 1))
        ch1.add_child(TOCEntry("Section 1.2", "ch1.html#s2", 1))
        
        tree.add_entry(ch1)
        tree.add_entry(TOCEntry("Chapter 2", "ch2.html", 0))
        
        flattened = tree.flatten()
        
        # Should include all entries in a flat list
        assert len(flattened) >= 4  # 2 chapters + 2 sections
        titles = [entry.title for entry in flattened]
        assert "Chapter 1" in titles
        assert "Section 1.1" in titles
        assert "Chapter 2" in titles
    
    def test_bookmark_tree_depth(self):
        """Test calculating bookmark tree depth."""
        tree = BookmarkTree()
        
        # Create deep hierarchy
        ch1 = TOCEntry("Chapter 1", "ch1.html", 0)
        sec1 = TOCEntry("Section 1.1", "ch1.html#s1", 1)
        subsec1 = TOCEntry("Subsection 1.1.1", "ch1.html#ss1", 2)
        
        sec1.add_child(subsec1)
        ch1.add_child(sec1)
        tree.add_entry(ch1)
        
        depth = tree.get_max_depth()
        
        assert depth >= 3  # 0, 1, 2 levels
