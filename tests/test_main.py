import pytest
import os
from click.testing import CliRunner
from unittest.mock import patch, Mock, AsyncMock
from aireview.main import main
from aireview.git_handler import FileChange

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
            FileChange(
                filename='test.py',
                content='test content',
                file_content='print("hello")\n'
            )
        ]
        yield mock

@pytest.fixture
def mock_openai():
    """Mock AsyncOpenAI client"""
    with patch('aireview.ai_reviewer.AsyncOpenAI') as mock:
        mock_client = Mock()
        mock_client.chat = Mock()
        mock_client.chat.completions = Mock()
        mock_client.chat.completions.create = AsyncMock(
            return_value=Mock(
                choices=[Mock(message=Mock(content="Test review content"))]
            )
        )
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
    # Get the output file path from the config
    import configparser
    config = configparser.ConfigParser()
    config.read(temp_config_file)
    output_file = config.get("review", "output", fallback="review.md")

    runner = CliRunner()
    result = runner.invoke(main, ['--config', temp_config_file])
    
    # Check CLI output
    assert result.exit_code == 0
    assert "Starting review for test.py" in result.output
    assert "Completed review for test.py" in result.output
    assert f"AI review written to {output_file}" in result.output
    
    # Check review file content
    assert os.path.exists(output_file)
    with open(output_file, 'r') as f:
        content = f.read()
        assert "Test review content" in content
    
    # Cleanup
    if os.path.exists(output_file):
        os.remove(output_file)

def test_main_cli_invalid_config():
    """Test CLI with invalid config file."""
    runner = CliRunner()
    result = runner.invoke(main, ['--config', 'nonexistent.config'])
    assert result.exit_code == 0  # Click catches the error
    assert "Error" in result.output