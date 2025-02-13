import pytest
from aireview.git_handler import GitHandler

def test_get_file_changes(temp_git_repo):
    """Test getting file changes from git repository."""
    handler = GitHandler()
    changes = handler.get_file_changes()
    
    assert len(changes) > 0
    assert changes[0].filename == "test.py"
    assert "Added: print" in changes[0].content

def test_parse_diff_output():
    """Test parsing git diff output."""
    diff_output = """diff --git a/test.py b/test.py
--- a/test.py
+++ b/test.py
@@ -1 +1 @@
-print("hello")
+print("hello world")
"""
    
    changes = GitHandler._parse_diff_output(diff_output)
    assert len(changes) == 1
    assert changes[0].filename == "test.py"
    assert "Removed: print(\"hello\")" in changes[0].content
    assert "Added: print(\"hello world\")" in changes[0].content