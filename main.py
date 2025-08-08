#!/usr/bin/env python3
"""
EPUB to PDF Converter - Phase 2 Entry Point
"""

import sys
import json
from pathlib import Path
import click
from src.converter import EPUBProcessor

@click.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option('--debug', is_flag=True, help='Show detailed processing information')
def main(input_file, debug):
    """Process EPUB file and display information."""
    try:
        # Process EPUB
        processor = EPUBProcessor(str(input_file))
        result = processor.process()
        
        # Display results
        metadata = result['metadata']
        click.echo("\n📚 EPUB Information")
        click.echo("=" * 50)
        click.echo(f"Title: {metadata.get('title', 'Unknown')}")
        click.echo(f"Author: {metadata.get('author', 'Unknown')}")
        click.echo(f"Language: {metadata.get('language', 'Unknown')}")
        
        if metadata.get('publisher'):
            click.echo(f"Publisher: {metadata['publisher']}")
        
        click.echo("\n📖 Content Structure")
        click.echo("=" * 50)
        click.echo(f"Chapters: {len(result['chapters'])}")
        click.echo(f"Images: {len(result['images'])}")
        click.echo(f"Stylesheets: {len(result['styles'])}")
        
        click.echo("\n📑 Table of Contents")
        click.echo("=" * 50)
        for item in result['toc'][:5]:  # Show first 5 items
            indent = "  " * item.get('level', 0)
            click.echo(f"{indent}• {item['title']}")
        
        if len(result['toc']) > 5:
            click.echo(f"  ... and {len(result['toc']) - 5} more")
        
        if debug:
            # Save full structure for debugging
            debug_file = input_file.stem + '_debug.json'
            with open(debug_file, 'w') as f:
                # Convert bytes to strings for JSON serialization
                debug_data = result.copy()
                debug_data['images'] = [
                    {k: v if k != 'data' else '<binary>' 
                     for k, v in img.items()}
                    for img in debug_data['images']
                ]
                json.dump(debug_data, f, indent=2, default=str)
            click.echo(f"\n💾 Debug data saved to: {debug_file}")
        
    except Exception as e:
        click.echo(f"Error processing EPUB: {e}", err=True)
        if debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()