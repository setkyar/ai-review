import pytest
from unittest.mock import Mock, patch
from aireview.ai_reviewer import AIReviewer
from aireview.git_handler import FileChange

@pytest.fixture
def mock_openai():
    """Mock OpenAI client responses."""
    with patch('aireview.ai_reviewer.OpenAI') as mock:
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Test review content"))]
        )
        mock.return_value = mock_client
        yield mock

def test_review_changes(mock_openai):
    """Test AI review generation."""
    reviewer = AIReviewer("test-model", "test-key")
    changes = [
        FileChange(
            filename="test.py",
            content="Added: print('hello world')"
        )
    ]
    
    reviews = reviewer.review_changes(
        changes,
        project_context="Test context",
        prompt_template="Test template"
    )
    
    assert len(reviews) == 1
    assert reviews[0].filename == "test.py"
    assert "Test review content" in reviews[0].content

def test_review_changes_api_error(mock_openai):
    """Test handling of API errors during review."""
    mock_openai.return_value.chat.completions.create.side_effect = Exception("API Error")
    
    reviewer = AIReviewer("test-model", "test-key")
    changes = [FileChange(filename="test.py", content="test content")]
    
    with pytest.raises(RuntimeError, match="OpenAI API error"):
        reviewer.review_changes(changes, "", "")