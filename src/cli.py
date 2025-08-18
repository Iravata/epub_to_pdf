#!/usr/bin/env python3
"""
EPUB to PDF Converter - Phase 5 CLI with enhanced error handling
Now with comprehensive Click-based CLI, error handling, and optimization!
"""

import sys
import click
from pathlib import Path
from src.optimized_converter import OptimizedEPUBProcessor
from src.enhanced_pdf_generator import EnhancedPDFGenerator
from src.error_handler import ErrorHandler
from src.validator import InputValidator

# Click command group for extensibility
@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """EPUB to PDF Converter with advanced features and robust error handling"""
    if ctx.invoked_subcommand is None:
        # If no subcommand, show help
        click.echo(ctx.get_help())

@main.command()
@click.argument('input_file', type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option('-o', '--output', type=click.Path(dir_okay=False, path_type=Path),
              help='Output PDF file path')
@click.option('--page-size', type=click.Choice(['letter', 'A4', 'A5'], case_sensitive=False),
              default='letter', show_default=True, help='PDF page size')
@click.option('--margins', type=click.Tuple([float, float, float, float]),
              metavar='TOP RIGHT BOTTOM LEFT',
              help='Page margins in inches (top, right, bottom, left)')
@click.option('--page-numbers/--no-page-numbers', default=False,
              help='Add page numbers to the PDF')
@click.option('--toc/--no-toc', default=True,
              help='Generate table of contents with bookmarks')
@click.option('--preserve-styles/--no-preserve-styles', default=True,
              help='Preserve CSS styles from EPUB')
@click.option('--header', help='Page header text')
@click.option('--footer', help='Page footer text')
@click.option('--streaming/--no-streaming', default=False,
              help='Use streaming mode for large files')
@click.option('--debug/--no-debug', default=False,
              help='Show detailed processing information and errors')
def convert(input_file, output, page_size, margins, page_numbers, toc, 
           preserve_styles, header, footer, streaming, debug):
    """Convert EPUB file to PDF with advanced formatting options and error handling.
    
    INPUT_FILE: Path to the EPUB file to convert
    """
    
    error_handler = ErrorHandler()
    
    try:
        # Validate input
        validator = InputValidator()
        is_valid, error_msg = validator.validate_epub(str(input_file))
        
        if not is_valid:
            raise click.ClickException(f"Invalid EPUB file: {error_msg}")
        
        # Determine output path
        if output:
            output_path = output
        else:
            output_path = input_file.with_suffix('.pdf')
        
        # Validate output path
        if not validator.validate_output_path(str(output_path)):
            sanitized = validator.sanitize_filename(output_path.name)
            output_path = output_path.parent / sanitized
            click.echo(f"⚠️  Output path sanitized to: {output_path}")
        
        # Validate options
        options_dict = {'page_size': page_size}
        if margins:
            if any(m < 0 for m in margins):
                raise click.BadParameter('Margins must be non-negative')
            if any(m > 5 for m in margins):
                raise click.BadParameter('Margins cannot exceed 5 inches')
            options_dict['margins'] = list(margins)
        
        if not validator.validate_options(options_dict):
            raise click.ClickException("Invalid conversion options")
        
        click.echo(f"📖 Processing EPUB: {input_file}")
        
        # Process EPUB with optimization and error handling
        with click.progressbar(length=100, label='Processing EPUB') as bar:
            processor = OptimizedEPUBProcessor(str(input_file), streaming=streaming)
            bar.update(30)
            
            epub_data = processor.process()
            bar.update(50)
        
        # Check for errors during processing
        if processor.error_handler.has_errors():
            error_summary = processor.error_handler.get_summary()
            if debug:
                click.echo(f"⚠️  Processing warnings/errors:\n{error_summary}", err=True)
            else:
                click.echo(f"⚠️  {processor.error_handler.get_error_count()} errors occurred (use --debug for details)")
        
        click.echo("✅ EPUB processed successfully")
        
        # Build options dict for PDF generation
        pdf_options = {
            'page_numbers': page_numbers,
            'preserve_styles': preserve_styles
        }
        
        if margins:
            pdf_options['margins'] = {
                'top': margins[0],
                'right': margins[1],
                'bottom': margins[2],
                'left': margins[3]
            }
        
        if header:
            pdf_options['header'] = header
        
        if footer:
            pdf_options['footer'] = footer
        
        # Generate PDF with error handling
        click.echo(f"\n📄 Generating enhanced PDF: {output_path}")
        
        with click.progressbar(length=100, label='Generating PDF') as bar:
            generator = EnhancedPDFGenerator(str(output_path), pdf_options)
            bar.update(20)
            
            generator.pdf_creator.set_page_size(page_size)
            bar.update(40)
            
            # Include TOC if requested
            if not toc:
                epub_data['toc'] = []  # Skip TOC generation
            
            success = generator.generate(epub_data)
            bar.update(100)
        
        if success:
            click.echo("✅ Enhanced PDF generated successfully!")
            click.echo(f"  • Output: {output_path}")
            if output_path.exists():
                click.echo(f"  • Size: {output_path.stat().st_size / 1024:.1f} KB")
            
            if page_numbers:
                click.echo("  • Page numbers: Enabled")
            if toc:
                click.echo("  • Table of contents: Generated")
            if preserve_styles:
                click.echo("  • CSS styles: Preserved")
            if streaming:
                click.echo("  • Streaming mode: Used")
        else:
            click.echo("❌ PDF generation failed", err=True)
            raise click.ClickException("PDF generation failed")
        
    except click.ClickException:
        raise  # Re-raise Click exceptions as-is
    except Exception as e:
        error_handler.log_error(str(e))
        if debug:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        raise click.ClickException(f"Conversion failed: {str(e)}")

@main.command()
@click.argument('input_files', nargs=-1, required=True, 
                type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, path_type=Path),
              default='.', help='Output directory for batch conversion')
@click.option('--page-size', type=click.Choice(['letter', 'A4', 'A5'], case_sensitive=False),
              default='letter', help='PDF page size for all files')
@click.option('--preserve-styles/--no-preserve-styles', default=True)
@click.option('--continue-on-error/--stop-on-error', default=True,
              help='Continue batch processing even if individual files fail')
def batch(input_files, output_dir, page_size, preserve_styles, continue_on_error):
    """Convert multiple EPUB files to PDF in batch mode with error recovery.
    
    INPUT_FILES: One or more EPUB files to convert
    """
    output_dir.mkdir(exist_ok=True)
    
    validator = InputValidator()
    results = []
    
    with click.progressbar(input_files, label='Converting EPUBs') as files:
        for epub_file in files:
            output_file = output_dir / epub_file.with_suffix('.pdf').name
            
            try:
                # Validate each file
                is_valid, error_msg = validator.validate_epub(str(epub_file))
                if not is_valid:
                    if continue_on_error:
                        click.echo(f"❌ Skipping {epub_file}: {error_msg}", err=True)
                        results.append({'file': epub_file, 'success': False, 'error': error_msg})
                        continue
                    else:
                        raise click.ClickException(f"Invalid EPUB: {error_msg}")
                
                processor = OptimizedEPUBProcessor(str(epub_file))
                epub_data = processor.process()
                
                options = {'preserve_styles': preserve_styles}
                generator = EnhancedPDFGenerator(str(output_file), options)
                generator.pdf_creator.set_page_size(page_size)
                
                success = generator.generate(epub_data)
                results.append({'file': epub_file, 'success': success})
                
            except Exception as e:
                if continue_on_error:
                    click.echo(f"❌ Failed to convert {epub_file}: {e}", err=True)
                    results.append({'file': epub_file, 'success': False, 'error': str(e)})
                else:
                    raise click.ClickException(f"Batch conversion failed at {epub_file}: {str(e)}")
    
    # Show summary
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    click.echo(f"\n📊 Batch conversion complete: {successful}/{total} files converted successfully")
    
    failed = [r for r in results if not r['success']]
    if failed:
        click.echo("\n❌ Failed conversions:")
        for result in failed[:5]:  # Show first 5 failures
            error_msg = result.get('error', 'Unknown error')
            click.echo(f"  • {result['file'].name}: {error_msg}")
        
        if len(failed) > 5:
            click.echo(f"  • ... and {len(failed) - 5} more")

if __name__ == "__main__":
    main()