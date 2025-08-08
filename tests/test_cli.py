import pytest
from src.cli import create_parser, validate_args

class TestCLI:
    def test_parser_requires_input_file(self):
        """Test CLI requires input file argument"""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])
    
    def test_parser_accepts_input_file(self):
        """Test CLI accepts input file"""
        parser = create_parser()
        args = parser.parse_args(['test.epub'])
        assert args.input == 'test.epub'
    
    def test_validate_args_checks_file_exists(self):
        """Test argument validation checks file existence"""
        args = type('Args', (), {'input': 'nonexistent.epub'})()
        is_valid, error = validate_args(args)
        assert is_valid == False
        assert "not found" in error.lower()