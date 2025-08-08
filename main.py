#!/usr/bin/env python3
"""
EPUB to PDF Converter - Phase 3
Now with actual PDF generation!
"""

import sys
from pathlib import Path
import click
from src.converter import EPUBProcessor
from src.pdf_generator import PDFGenerator

@click.command()
@click.argument('input_file', type=click.Path(exists=True, dir_okay=False))
@click.option(
    '--output', '-o',
    type=click.Path(dir_okay=False),
    help='Output PDF file path (auto-generated if not specified)'
)
@click.option(
    '--page-size',
    type=click.Choice(['letter', 'A4', 'A5']),
    default='letter',
    help='PDF page size'
)
@click.option(
    '--debug',
    is_flag=True,
    help='Show detailed processing information'
)
def main(input_file, output, page_size, debug):
    """Convert EPUB files to PDF format with basic formatting."""
    
    # Determine output path
    if output:
        output_path = output
    else:
        # Auto-generate output filename
        input_path = Path(input_file)
        output_path = input_path.with_suffix('.pdf')
    
    try:
        click.echo(f"📖 Processing EPUB: {input_file}")
        
        # Process EPUB (Phase 2)
        processor = EPUBProcessor(input_file)
        epub_data = processor.process()
        
        click.echo("✅ EPUB processed successfully")
        click.echo(f"  • Chapters: {len(epub_data['chapters'])}")
        click.echo(f"  • Images: {len(epub_data['images'])}")
        
        # Generate PDF (Phase 3)
        click.echo(f"\n📄 Generating PDF: {output_path}")
        
        # Show progress bar for PDF generation
        generator = PDFGenerator(str(output_path), page_size)
        
        with click.progressbar(epub_data['chapters'], label='Converting chapters') as chapters:
            # Set metadata first
            generator._add_metadata(epub_data['metadata'])
            
            # Cache images
            generator._cache_images(epub_data.get('images', []))
            
            # Process chapters with progress
            for i, chapter in enumerate(chapters):
                if i > 0:
                    generator.pdf_creator.add_page()
                generator._process_chapter(chapter)
        
        # Save PDF
        generator.pdf_creator.save()
        
        click.echo("✅ PDF generated successfully!")
        click.echo(f"  • Output: {output_path}")
        click.echo(f"  • Size: {Path(output_path).stat().st_size / 1024:.1f} KB")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        if debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()