import pytest
from click.testing import CliRunner
from unittest.mock import patch
from aireview.main import main

@pytest.fixture
def mock_git_no_changes():
    """Mock GitHandler to return no changes"""
    with patch('aireview.git_handler.GitHandler.get_file_changes') as mock:
        mock.return_value = []
        yield mock

@pytest.fixture
def mock_git_with_changes():
    """Mock GitHandler to return some changes"""
    with patch('aireview.git_handler.GitHandler.get_file_changes') as mock:
        mock.return_value = [
            type('FileChange', (), {'filename': 'test.py', 'content': 'test content'})()
        ]
        yield mock

@pytest.fixture
def mock_openai():
    """Mock OpenAI client"""
    with patch('aireview.ai_reviewer.OpenAI') as mock:
        mock_client = type('MockClient', (), {
            'chat': type('MockChat', (), {
                'completions': type('MockCompletions', (), {
                    'create': lambda **kwargs: type('MockResponse', (), {
                        'choices': [type('MockChoice', (), {
                            'message': type('MockMessage', (), {'content': 'Test review'})
                        })()]
                    })()
                })()
            })()
        })()
        mock.return_value = mock_client
        yield mock

def test_main_cli_no_changes(temp_config_file, mock_git_no_changes):
    """Test CLI with no git changes."""
    runner = CliRunner()
    result = runner.invoke(main, ['--config', temp_config_file])
    assert result.exit_code == 0
    assert "No changes found" in result.output

def test_main_cli_with_changes(temp_config_file, mock_git_with_changes, mock_openai):
    """Test CLI with git changes."""
    runner = CliRunner()
    result = runner.invoke(main, ['--config', temp_config_file])
    assert result.exit_code == 0
    assert "Getting review for test.py" in result.output

def test_main_cli_invalid_config():
    """Test CLI with invalid config file."""
    runner = CliRunner()
    result = runner.invoke(main, ['--config', 'nonexistent.config'])
    assert result.exit_code == 0  # Click catches the error
    assert "Error" in result.output