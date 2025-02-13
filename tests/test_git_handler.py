import pytest
from unittest.mock import patch, Mock
import subprocess
from aireview.git_handler import GitHandler, FileChange

def test_get_staged_changes():
    """Test getting staged changes."""
    with patch('subprocess.run') as mock_run:
        # Mock staged changes
        mock_run.return_value = Mock(
            stdout="""diff --git a/test.py b/test.py
+++ b/test.py
-old line
+new line
diff --git a/example.js b/example.js
+++ b/example.js
+console.log('hello');""",
            stderr=""
        )
        
        changes = GitHandler.get_file_changes()
        assert len(changes) == 2
        
        # Check first file changes
        py_change = next(c for c in changes if c.filename == "test.py")
        assert "Added: new line" in py_change.content
        assert "Removed: old line" in py_change.content
        
        # Check second file changes
        js_change = next(c for c in changes if c.filename == "example.js")
        assert "Added: console.log('hello');" in js_change.content

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

def test_extract_filename_valid_section():
    """Test extracting filename from a valid diff section."""
    section = """diff --git a/test.py b/test.py
index 1234567..89abcdef 100644
--- a/test.py
+++ b/test.py
@@ -1,1 +1,1 @@"""
    
    filename = GitHandler._extract_filename(section)
    assert filename == "test.py"

def test_extract_changes_with_additions_and_removals():
    """Test extracting both added and removed lines."""
    section = """diff --git a/test.py b/test.py
index 1234567..89abcdef 100644
--- a/test.py
+++ b/test.py
@@ -1,1 +1,1 @@
-old code
+new code
+more new code"""
    
    changes = GitHandler._extract_changes(section)
    assert "Added: new code" in changes
    assert "Added: more new code" in changes
    assert "Removed: old code" in changes