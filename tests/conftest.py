import pytest
from pathlib import Path
import zipfile
import base64

@pytest.fixture
def sample_epub(tmp_path):
    """Create a minimal valid EPUB for testing"""
    epub_path = tmp_path / "test.epub"
    
    # Create minimal EPUB structure
    with zipfile.ZipFile(epub_path, 'w') as epub:
        # Add mimetype
        epub.writestr("mimetype", "application/epub+zip")
        
        # Add container.xml
        container = '''<?xml version="1.0"?>
        <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
            <rootfiles>
                <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
            </rootfiles>
        </container>'''
        epub.writestr("META-INF/container.xml", container)
        
        # Add minimal content.opf
        content_opf = '''<?xml version="1.0"?>
        <package xmlns="http://www.idpf.org/2007/opf" version="2.0">
            <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
                <dc:title>Test Book</dc:title>
                <dc:creator>Test Author</dc:creator>
                <dc:language>en</dc:language>
                <dc:publisher>Test Publisher</dc:publisher>
                <dc:date>2024-01-01</dc:date>
                <dc:identifier>978-0-123456-78-9</dc:identifier>
                <dc:description>Test Description</dc:description>
            </metadata>
            <manifest>
                <item id="chapter1" href="chapter1.html" media-type="application/xhtml+xml"/>
            </manifest>
            <spine>
                <itemref idref="chapter1"/>
            </spine>
        </package>'''
        epub.writestr("content.opf", content_opf)
        
        # Add sample chapter
        chapter = '''<html><body><h1>Chapter 1</h1><p>Content</p></body></html>'''
        epub.writestr("chapter1.html", chapter)
    
    return str(epub_path)

@pytest.fixture
def minimal_epub(tmp_path):
    """Create minimal EPUB with missing metadata"""
    epub_path = tmp_path / "minimal.epub"
    
    with zipfile.ZipFile(epub_path, 'w') as epub:
        epub.writestr("mimetype", "application/epub+zip")
        
        container = '''<?xml version="1.0"?>
        <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
            <rootfiles>
                <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
            </rootfiles>
        </container>'''
        epub.writestr("META-INF/container.xml", container)
        
        # Minimal content.opf with missing metadata
        content_opf = '''<?xml version="1.0"?>
        <package xmlns="http://www.idpf.org/2007/opf" version="2.0">
            <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
            </metadata>
            <manifest>
                <item id="chapter1" href="chapter1.html" media-type="application/xhtml+xml"/>
            </manifest>
            <spine>
                <itemref idref="chapter1"/>
            </spine>
        </package>'''
        epub.writestr("content.opf", content_opf)
        
        chapter = '''<html><body><h1>Chapter 1</h1><p>Content</p></body></html>'''
        epub.writestr("chapter1.html", chapter)
    
    return str(epub_path)

@pytest.fixture
def multi_author_epub(tmp_path):
    """Create EPUB with multiple authors"""
    epub_path = tmp_path / "multi_author.epub"
    
    with zipfile.ZipFile(epub_path, 'w') as epub:
        epub.writestr("mimetype", "application/epub+zip")
        
        container = '''<?xml version="1.0"?>
        <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
            <rootfiles>
                <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
            </rootfiles>
        </container>'''
        epub.writestr("META-INF/container.xml", container)
        
        content_opf = '''<?xml version="1.0"?>
        <package xmlns="http://www.idpf.org/2007/opf" version="2.0">
            <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
                <dc:title>Multi-Author Book</dc:title>
                <dc:creator>First Author</dc:creator>
                <dc:creator>Second Author</dc:creator>
                <dc:creator>Third Author</dc:creator>
                <dc:language>en</dc:language>
            </metadata>
            <manifest>
                <item id="chapter1" href="chapter1.html" media-type="application/xhtml+xml"/>
            </manifest>
            <spine>
                <itemref idref="chapter1"/>
            </spine>
        </package>'''
        epub.writestr("content.opf", content_opf)
        
        chapter = '''<html><body><h1>Chapter 1</h1><p>Content</p></body></html>'''
        epub.writestr("chapter1.html", chapter)
    
    return str(epub_path)

@pytest.fixture
def epub_with_images(tmp_path):
    """Create EPUB with embedded images"""
    epub_path = tmp_path / "images.epub"
    
    with zipfile.ZipFile(epub_path, 'w') as epub:
        epub.writestr("mimetype", "application/epub+zip")
        
        container = '''<?xml version="1.0"?>
        <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
            <rootfiles>
                <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
            </rootfiles>
        </container>'''
        epub.writestr("META-INF/container.xml", container)
        
        content_opf = '''<?xml version="1.0"?>
        <package xmlns="http://www.idpf.org/2007/opf" version="2.0">
            <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
                <dc:title>Book with Images</dc:title>
                <dc:creator>Test Author</dc:creator>
            </metadata>
            <manifest>
                <item id="chapter1" href="chapter1.html" media-type="application/xhtml+xml"/>
                <item id="img1" href="images/test.jpg" media-type="image/jpeg"/>
                <item id="img2" href="images/test.png" media-type="image/png"/>
            </manifest>
            <spine>
                <itemref idref="chapter1"/>
            </spine>
        </package>'''
        epub.writestr("content.opf", content_opf)
        
        chapter = '''<html><body><h1>Chapter 1</h1><img src="images/test.jpg"/></body></html>'''
        epub.writestr("chapter1.html", chapter)
        
        # Add dummy images (1x1 pixel)
        jpeg_data = base64.b64decode('/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA8A/9k=')
        png_data = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==')
        
        epub.writestr("images/test.jpg", jpeg_data)
        epub.writestr("images/test.png", png_data)
    
    return str(epub_path)

@pytest.fixture
def epub_with_ncx(tmp_path):
    """Create EPUB with NCX navigation"""
    epub_path = tmp_path / "ncx.epub"
    
    with zipfile.ZipFile(epub_path, 'w') as epub:
        epub.writestr("mimetype", "application/epub+zip")
        
        container = '''<?xml version="1.0"?>
        <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
            <rootfiles>
                <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
            </rootfiles>
        </container>'''
        epub.writestr("META-INF/container.xml", container)
        
        content_opf = '''<?xml version="1.0"?>
        <package xmlns="http://www.idpf.org/2007/opf" version="2.0">
            <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
                <dc:title>Book with NCX</dc:title>
                <dc:creator>Test Author</dc:creator>
            </metadata>
            <manifest>
                <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
                <item id="chapter1" href="chapter1.html" media-type="application/xhtml+xml"/>
                <item id="chapter2" href="chapter2.html" media-type="application/xhtml+xml"/>
            </manifest>
            <spine toc="ncx">
                <itemref idref="chapter1"/>
                <itemref idref="chapter2"/>
            </spine>
        </package>'''
        epub.writestr("content.opf", content_opf)
        
        ncx = '''<?xml version="1.0" encoding="UTF-8"?>
        <ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
            <head>
                <meta name="dtb:uid" content="123"/>
            </head>
            <docTitle>
                <text>Book with NCX</text>
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
        epub.writestr("toc.ncx", ncx)
        
        epub.writestr("chapter1.html", '''<html><body><h1>Chapter 1</h1><p>Content</p></body></html>''')
        epub.writestr("chapter2.html", '''<html><body><h1>Chapter 2</h1><p>Content</p></body></html>''')
    
    return str(epub_path)

@pytest.fixture
def epub3_with_nav(tmp_path):
    """Create EPUB3 with nav document"""
    epub_path = tmp_path / "epub3_nav.epub"
    
    with zipfile.ZipFile(epub_path, 'w') as epub:
        epub.writestr("mimetype", "application/epub+zip")
        
        container = '''<?xml version="1.0"?>
        <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
            <rootfiles>
                <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
            </rootfiles>
        </container>'''
        epub.writestr("META-INF/container.xml", container)
        
        content_opf = '''<?xml version="1.0"?>
        <package xmlns="http://www.idpf.org/2007/opf" version="3.0">
            <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
                <dc:title>EPUB3 Book</dc:title>
                <dc:creator>Test Author</dc:creator>
            </metadata>
            <manifest>
                <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
                <item id="chapter1" href="chapter1.html" media-type="application/xhtml+xml"/>
            </manifest>
            <spine>
                <itemref idref="chapter1"/>
            </spine>
        </package>'''
        epub.writestr("content.opf", content_opf)
        
        nav = '''<?xml version="1.0" encoding="UTF-8"?>
        <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
            <head>
                <title>Navigation</title>
            </head>
            <body>
                <nav epub:type="toc">
                    <ol>
                        <li><a href="chapter1.html">Chapter 1</a></li>
                    </ol>
                </nav>
            </body>
        </html>'''
        epub.writestr("nav.xhtml", nav)
        
        chapter = '''<html><body><h1>Chapter 1</h1><p>Content</p></body></html>'''
        epub.writestr("chapter1.html", chapter)
    
    return str(epub_path)

@pytest.fixture
def epub_without_toc(tmp_path):
    """Create EPUB without TOC"""
    epub_path = tmp_path / "no_toc.epub"
    
    with zipfile.ZipFile(epub_path, 'w') as epub:
        epub.writestr("mimetype", "application/epub+zip")
        
        container = '''<?xml version="1.0"?>
        <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
            <rootfiles>
                <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
            </rootfiles>
        </container>'''
        epub.writestr("META-INF/container.xml", container)
        
        content_opf = '''<?xml version="1.0"?>
        <package xmlns="http://www.idpf.org/2007/opf" version="2.0">
            <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
                <dc:title>Book without TOC</dc:title>
                <dc:creator>Test Author</dc:creator>
            </metadata>
            <manifest>
                <item id="chapter1" href="chapter1.html" media-type="application/xhtml+xml"/>
                <item id="chapter2" href="chapter2.html" media-type="application/xhtml+xml"/>
            </manifest>
            <spine>
                <itemref idref="chapter1"/>
                <itemref idref="chapter2"/>
            </spine>
        </package>'''
        epub.writestr("content.opf", content_opf)
        
        epub.writestr("chapter1.html", '''<html><body><h1>First Chapter</h1><p>Content</p></body></html>''')
        epub.writestr("chapter2.html", '''<html><body><h2>Second Chapter</h2><p>Content</p></body></html>''')
    
    return str(epub_path)

@pytest.fixture
def nested_toc_epub(tmp_path):
    """Create EPUB with nested TOC structure"""
    epub_path = tmp_path / "nested_toc.epub"
    
    with zipfile.ZipFile(epub_path, 'w') as epub:
        epub.writestr("mimetype", "application/epub+zip")
        
        container = '''<?xml version="1.0"?>
        <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
            <rootfiles>
                <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
            </rootfiles>
        </container>'''
        epub.writestr("META-INF/container.xml", container)
        
        content_opf = '''<?xml version="1.0"?>
        <package xmlns="http://www.idpf.org/2007/opf" version="2.0">
            <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
                <dc:title>Book with Nested TOC</dc:title>
                <dc:creator>Test Author</dc:creator>
            </metadata>
            <manifest>
                <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
                <item id="chapter1" href="chapter1.html" media-type="application/xhtml+xml"/>
                <item id="chapter1_1" href="chapter1_1.html" media-type="application/xhtml+xml"/>
            </manifest>
            <spine toc="ncx">
                <itemref idref="chapter1"/>
                <itemref idref="chapter1_1"/>
            </spine>
        </package>'''
        epub.writestr("content.opf", content_opf)
        
        ncx = '''<?xml version="1.0" encoding="UTF-8"?>
        <ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
            <head>
                <meta name="dtb:uid" content="123"/>
            </head>
            <docTitle>
                <text>Book with Nested TOC</text>
            </docTitle>
            <navMap>
                <navPoint id="navpoint1" playOrder="1">
                    <navLabel>
                        <text>Chapter 1</text>
                    </navLabel>
                    <content src="chapter1.html"/>
                    <navPoint id="navpoint1_1" playOrder="2">
                        <navLabel>
                            <text>Section 1.1</text>
                        </navLabel>
                        <content src="chapter1_1.html"/>
                    </navPoint>
                </navPoint>
            </navMap>
        </ncx>'''
        epub.writestr("toc.ncx", ncx)
        
        epub.writestr("chapter1.html", '''<html><body><h1>Chapter 1</h1><p>Content</p></body></html>''')
        epub.writestr("chapter1_1.html", '''<html><body><h2>Section 1.1</h2><p>Content</p></body></html>''')
    
    return str(epub_path)

@pytest.fixture
def nested_epub(nested_toc_epub):
    """Create EPUB with nested structure"""
    return nested_toc_epub

@pytest.fixture
def epub_with_styles(tmp_path):
    """Create EPUB with CSS stylesheets"""
    epub_path = tmp_path / "styles.epub"
    
    with zipfile.ZipFile(epub_path, 'w') as epub:
        epub.writestr("mimetype", "application/epub+zip")
        
        container = '''<?xml version="1.0"?>
        <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
            <rootfiles>
                <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
            </rootfiles>
        </container>'''
        epub.writestr("META-INF/container.xml", container)
        
        content_opf = '''<?xml version="1.0"?>
        <package xmlns="http://www.idpf.org/2007/opf" version="2.0">
            <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
                <dc:title>Styled Book</dc:title>
                <dc:creator>Test Author</dc:creator>
            </metadata>
            <manifest>
                <item id="chapter1" href="chapter1.html" media-type="application/xhtml+xml"/>
                <item id="style1" href="styles/main.css" media-type="text/css"/>
            </manifest>
            <spine>
                <itemref idref="chapter1"/>
            </spine>
        </package>'''
        epub.writestr("content.opf", content_opf)
        
        chapter = '''<html><head><link rel="stylesheet" href="styles/main.css"/></head><body><h1>Chapter 1</h1></body></html>'''
        epub.writestr("chapter1.html", chapter)
        
        css = '''body { font-family: serif; } h1 { color: #333; }'''
        epub.writestr("styles/main.css", css)
    
    return str(epub_path)

@pytest.fixture
def epub_with_fonts(tmp_path):
    """Create EPUB with fonts"""
    epub_path = tmp_path / "fonts.epub"
    
    with zipfile.ZipFile(epub_path, 'w') as epub:
        epub.writestr("mimetype", "application/epub+zip")
        
        container = '''<?xml version="1.0"?>
        <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
            <rootfiles>
                <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
            </rootfiles>
        </container>'''
        epub.writestr("META-INF/container.xml", container)
        
        content_opf = '''<?xml version="1.0"?>
        <package xmlns="http://www.idpf.org/2007/opf" version="2.0">
            <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
                <dc:title>Book with Fonts</dc:title>
                <dc:creator>Test Author</dc:creator>
            </metadata>
            <manifest>
                <item id="chapter1" href="chapter1.html" media-type="application/xhtml+xml"/>
                <item id="font1" href="fonts/test.ttf" media-type="font/truetype"/>
            </manifest>
            <spine>
                <itemref idref="chapter1"/>
            </spine>
        </package>'''
        epub.writestr("content.opf", content_opf)
        
        chapter = '''<html><body><h1>Chapter 1</h1></body></html>'''
        epub.writestr("chapter1.html", chapter)
        
        # Add dummy font file
        epub.writestr("fonts/test.ttf", b"dummy font data")
    
    return str(epub_path)