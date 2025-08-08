from PIL import Image
import io
from typing import Dict, Any, Optional

class ImageEmbedder:
    """Handle image embedding in PDF (KISS approach)"""
    
    def prepare_image(self, image_data: bytes, 
                     max_width: int = 500,
                     max_height: int = 700) -> Optional[Dict[str, Any]]:
        """Prepare image for PDF embedding"""
        if not image_data:
            return None
        
        try:
            # Open image with PIL
            img = Image.open(io.BytesIO(image_data))
            
            # Get original dimensions
            orig_width, orig_height = img.size
            
            # Calculate scaling to fit within max dimensions
            scale = min(
                max_width / orig_width,
                max_height / orig_height,
                1.0  # Don't upscale
            )
            
            if scale < 1.0:
                # Resize image
                new_width = int(orig_width * scale)
                new_height = int(orig_height * scale)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to appropriate format
            output = io.BytesIO()
            format = 'JPEG' if img.mode == 'RGB' else 'PNG'
            
            # Handle transparency for PNG
            if format == 'PNG' and img.mode == 'RGBA':
                img.save(output, format=format)
            else:
                # Convert to RGB for JPEG
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(output, format='JPEG', quality=85)
            
            return {
                'data': output.getvalue(),
                'width': img.width,
                'height': img.height,
                'format': format,
                'aspect_ratio_preserved': True
            }
            
        except Exception as e:
            # KISS: Just skip problematic images
            return None