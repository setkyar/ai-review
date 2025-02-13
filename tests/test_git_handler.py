import pytest
from unittest.mock import patch, Mock
import subprocess
from aireview.git_handler import GitHandler, FileChange

def test_get_staged_changes():
    """Test getting staged changes with file content."""
    with patch('subprocess.run') as mock_run:
        def mock_command(*args, **kwargs):
            if 'diff' in args[0]:
                return Mock(
                    stdout="""diff --git a/test.py b/test.py
+++ b/test.py
-old line
+new line
diff --git a/example.js b/example.js
+++ b/example.js
+console.log('hello');""",
                    stderr=""
                )
            elif 'show' in args[0]:
                # Here's the fix: Check the exact filename in the command
                cmd_str = ' '.join(args[0])
                if ':test.py' in cmd_str:
                    return Mock(stdout="print('hello world')\n", stderr="")
                elif ':example.js' in cmd_str:
                    return Mock(stdout="console.log('hello');\n", stderr="")
        
        mock_run.side_effect = mock_command
        
        changes = GitHandler.get_file_changes()
        assert len(changes) == 2
        
        # Check first file changes
        py_change = next(c for c in changes if c.filename == "test.py")
        assert "Added: new line" in py_change.content
        assert "Removed: old line" in py_change.content
        assert py_change.file_content == "print('hello world')\n"
        
        # Check second file changes
        js_change = next(c for c in changes if c.filename == "example.js")
        assert "Added: console.log('hello');" in js_change.content
        assert js_change.file_content == "console.log('hello');\n"

def test_get_file_changes_no_staged_changes():
    """Test when there are no staged changes."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(stdout="", stderr="")
        
        changes = GitHandler.get_file_changes()
        assert len(changes) == 0

def test_get_file_changes_git_error():
    """Test handling of git command errors."""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(
            1, 'git', stderr="git error"
        )
        
        with pytest.raises(RuntimeError) as exc_info:
            GitHandler.get_file_changes()
        assert "Git command failed" in str(exc_info.value)

def test_get_file_changes_with_new_file():
    """Test handling of new files where git show might fail."""
    with patch('subprocess.run') as mock_run:
        def mock_command(*args, **kwargs):
            if 'diff' in args[0]:
                return Mock(
                    stdout="""diff --git a/new.py b/new.py
+++ b/new.py
+print('new file')""",
                    stderr=""
                )
            elif 'show' in args[0]:
                raise subprocess.CalledProcessError(128, 'git', stderr="file not found")
        
        mock_run.side_effect = mock_command
        
        changes = GitHandler.get_file_changes()
        assert len(changes) == 1
        assert changes[0].filename == "new.py"
        assert changes[0].file_content is None  # New file has no previous content