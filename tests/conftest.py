import pytest
from pathlib import Path
import tempfile
import os

@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    config_content = """
[ai]
model = test-model
api_key = test-key
base_url = http://test.url

[review]
output = review.md

[context]
project_context = Test project context

[prompt]
prompt_template = Test prompt template
"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.config') as f:
        f.write(config_content)
        config_path = f.name
    
    yield config_path
    os.unlink(config_path)

@pytest.fixture
def temp_git_repo():
    """Create a temporary git repository with some changes."""
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        os.system('git init')
        
        # Create and modify a test file
        test_file = Path(temp_dir) / 'test.py'
        test_file.write_text('print("hello")\n')
        
        os.system('git add test.py')
        os.system('git commit -m "Initial commit"')
        
        # Make some changes
        test_file.write_text('print("hello world")\n')
        
        yield temp_dir
        os.system(f'rm -rf {temp_dir}')