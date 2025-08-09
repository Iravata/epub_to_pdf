import re
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

class InputValidator:
    """Validate and sanitize input (KISS principle)"""
    
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
    VALID_PAGE_SIZES = ['letter', 'A4', 'A5']
    INVALID_CHARS = r'[<>:"/\\|?*]'
    
    def validate_file_size(self, file_path: str, size: int) -> bool:
        """Validate file size is within limits"""
        if size > self.MAX_FILE_SIZE:
            return False
        return True
    
    def validate_output_path(self, output_path: str) -> bool:
        """Validate output path"""
        path = Path(output_path)
        
        # Check extension
        if path.suffix.lower() != '.pdf':
            return False
        
        # Check parent directory exists
        if not path.parent.exists():
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
            except:
                return False
        
        # Check write permissions
        try:
            test_file = path.parent / '.test_write'
            test_file.touch()
            test_file.unlink()
            return True
        except:
            return False
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem"""
        # Replace invalid characters
        sanitized = re.sub(self.INVALID_CHARS, '_', filename)
        
        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip('. ')
        
        # Ensure not empty
        if not sanitized:
            sanitized = 'output'
        
        # Ensure has .pdf extension
        if not sanitized.endswith('.pdf'):
            sanitized += '.pdf'
        
        return sanitized
    
    def validate_options(self, options: Dict[str, Any]) -> bool:
        """Validate conversion options"""
        # Validate page size
        if 'page_size' in options:
            if options['page_size'] not in self.VALID_PAGE_SIZES:
                return False
        
        # Validate margins
        if 'margins' in options:
            margins = options['margins']
            if not isinstance(margins, list) or len(margins) != 4:
                return False
            
            for margin in margins:
                if not isinstance(margin, (int, float)) or margin < 0:
                    return False
        
        return True
    
    def validate_epub(self, epub_path: str) -> Tuple[bool, Optional[str]]:
        """Comprehensive EPUB validation"""
        path = Path(epub_path)
        
        # Check file exists
        if not path.exists():
            return False, "File not found"
        
        # Check extension
        if path.suffix.lower() != '.epub':
            return False, "Not an EPUB file"
        
        # Check file size
        size = path.stat().st_size
        if not self.validate_file_size(str(path), size):
            return False, f"File too large (max {self.MAX_FILE_SIZE / 1024 / 1024}MB)"
        
        # Check ZIP signature
        try:
            with open(path, 'rb') as f:
                signature = f.read(2)
                if signature != b'PK':
                    return False, "Invalid EPUB format"
        except Exception as e:
            return False, f"Cannot read file: {e}"
        
        return True, None