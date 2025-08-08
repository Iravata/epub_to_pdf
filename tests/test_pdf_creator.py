import pytest
from pathlib import Path
from src.pdf_creator import PDFCreator
import PyPDF2

class TestPDFCreator:
    def test_create_empty_pdf(self, tmp_path):
        """Test creation of empty PDF file"""
        output_path = tmp_path / "test.pdf"
        creator = PDFCreator(str(output_path))
        creator.save()
        
        assert output_path.exists()
        assert output_path.stat().st_size > 0
    
    def test_add_metadata(self, tmp_path):
        """Test adding metadata to PDF"""
        output_path = tmp_path / "test.pdf"
        creator = PDFCreator(str(output_path))
        
        metadata = {
            'title': 'Test Book',
            'author': 'Test Author',
            'subject': 'Testing'
        }
        creator.set_metadata(metadata)
        creator.save()
        
        # Verify metadata
        with open(output_path, 'rb') as f:
            pdf = PyPDF2.PdfReader(f)
            info = pdf.metadata
            assert info.title == 'Test Book'
            assert info.author == 'Test Author'
    
    def test_add_page_with_text(self, tmp_path):
        """Test adding page with text content"""
        output_path = tmp_path / "test.pdf"
        creator = PDFCreator(str(output_path))
        
        creator.add_page()
        creator.add_text("Hello, World!")
        creator.save()
        
        # Verify page count
        with open(output_path, 'rb') as f:
            pdf = PyPDF2.PdfReader(f)
            assert len(pdf.pages) == 1
    
    def test_set_page_size(self, tmp_path):
        """Test setting custom page size"""
        output_path = tmp_path / "test.pdf"
        creator = PDFCreator(str(output_path))
        
        creator.set_page_size('A4')
        creator.add_page()
        creator.save()
        
        assert output_path.exists()