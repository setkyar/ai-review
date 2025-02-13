import pytest
from unittest.mock import Mock, patch, AsyncMock
from aireview.ai_reviewer import AIReviewer
from aireview.git_handler import FileChange

@pytest.fixture
def mock_openai():
    """Mock AsyncOpenAI client responses."""
    with patch('aireview.ai_reviewer.AsyncOpenAI') as mock:
        mock_client = Mock()
        # Use AsyncMock for async methods
        mock_client.chat = Mock()
        mock_client.chat.completions = Mock()
        mock_client.chat.completions.create = AsyncMock(
            return_value=Mock(
                choices=[Mock(message=Mock(content="Mock review content"))]
            )
        )
        mock.return_value = mock_client
        yield mock

@pytest.mark.asyncio
async def test_review_changes_with_file_content(mock_openai):
    """Test AI review generation with file content."""
    reviewer = AIReviewer("test-model", "test-key")
    changes = [
        FileChange(
            filename="test.py",
            content="Added: print('hello world')",
            file_content="print('hello')\nprint('hello world')"
        )
    ]
    
    reviews = await reviewer.review_changes(
        changes,
        project_context="Test context",
        prompt_template="Test template"
    )
    
    # Verify the review was created
    assert len(reviews) == 1
    assert reviews[0].filename == "test.py"
    
    # Verify the prompt sent to the API includes file content
    api_call_args = mock_openai.return_value.chat.completions.create.call_args
    prompt_sent = api_call_args[1]['messages'][1]['content']
    assert "Current file content:" in prompt_sent
    assert "print('hello')" in prompt_sent

@pytest.mark.asyncio
async def test_review_changes_without_file_content(mock_openai):
    """Test AI review generation without file content."""
    reviewer = AIReviewer("test-model", "test-key")
    changes = [
        FileChange(
            filename="test.py",
            content="Added: print('hello world')",
            file_content=None  # No file content
        )
    ]
    
    reviews = await reviewer.review_changes(
        changes,
        project_context="Test context",
        prompt_template="Test template"
    )
    
    # Verify the review was created
    assert len(reviews) == 1
    assert reviews[0].filename == "test.py"
    
    # Verify the prompt sent to the API doesn't include file content section
    api_call_args = mock_openai.return_value.chat.completions.create.call_args
    prompt_sent = api_call_args[1]['messages'][1]['content']
    assert "Current file content:" not in prompt_sent
    assert changes[0].content in prompt_sent

@pytest.mark.asyncio
async def test_review_changes_api_error(mock_openai):
    """Test handling of API errors during review."""
    mock_openai.return_value.chat.completions.create.side_effect = Exception("API Error")
    
    reviewer = AIReviewer("test-model", "test-key")
    changes = [FileChange(filename="test.py", content="test content")]
    
    with pytest.raises(RuntimeError, match="OpenAI API error"):
        await reviewer.review_changes(changes, "", "")