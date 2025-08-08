from pathlib import Path

class EPUBValidator:
    """Simple EPUB file validator (KISS principle)"""
    
    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.error = None
    
    def is_valid(self):
        """Check if file is a valid EPUB"""
        if not self.filepath.exists():
            self.error = "File not found"
            return False
        
        if self.filepath.suffix.lower() != '.epub':
            self.error = "Not an EPUB file"
            return False
        
        # Check for ZIP signature (EPUB is a ZIP file)
        try:
            with open(self.filepath, 'rb') as f:
                signature = f.read(2)
                if signature != b'PK':
                    self.error = "Invalid EPUB format"
                    return False
        except Exception as e:
            self.error = str(e)
            return False
        
        return True
    
    def get_error(self):
        """Get validation error message"""
        return self.error