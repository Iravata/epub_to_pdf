import pytest
from PIL import Image
import io
from src.image_embedder import ImageEmbedder

class TestImageEmbedder:
    @pytest.fixture
    def sample_jpeg(self):
        """Create a sample JPEG image for testing"""
        img = Image.new('RGB', (100, 100), color='red')
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        return buffer.getvalue()
    
    @pytest.fixture
    def sample_png(self):
        """Create a sample PNG image for testing"""
        img = Image.new('RGBA', (100, 100), color='blue')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    @pytest.fixture
    def large_image(self):
        """Create a large image for resize testing"""
        img = Image.new('RGB', (1000, 1000), color='green')
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        return buffer.getvalue()
    
    def test_embed_jpeg_image(self, sample_jpeg):
        """Test embedding JPEG images"""
        embedder = ImageEmbedder()
        result = embedder.prepare_image(sample_jpeg, max_width=500)
        
        assert result['width'] <= 500
        assert result['format'] == 'JPEG'
        assert result['data'] is not None
    
    def test_embed_png_image(self, sample_png):
        """Test embedding PNG images"""
        embedder = ImageEmbedder()
        result = embedder.prepare_image(sample_png, max_width=500)
        
        assert result['width'] <= 500
        assert result['format'] == 'PNG'
    
    def test_resize_large_image(self, large_image):
        """Test resizing of large images"""
        embedder = ImageEmbedder()
        result = embedder.prepare_image(large_image, max_width=400)
        
        assert result['width'] <= 400
        assert result['aspect_ratio_preserved'] == True
    
    def test_handle_missing_image(self):
        """Test handling of missing images"""
        embedder = ImageEmbedder()
        result = embedder.prepare_image(b'', max_width=500)
        
        assert result is None