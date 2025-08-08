import argparse
from pathlib import Path

def create_parser():
    """Create argument parser (KISS - minimal options)"""
    parser = argparse.ArgumentParser(
        description='Convert EPUB to PDF',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'input',
        help='Input EPUB file path'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output PDF file path (optional)',
        default=None
    )
    
    return parser

def validate_args(args):
    """Validate command line arguments"""
    input_path = Path(args.input)
    
    if not input_path.exists():
        return False, f"Input file not found: {args.input}"
    
    if input_path.suffix.lower() != '.epub':
        return False, f"Input file must be an EPUB: {args.input}"
    
    return True, None