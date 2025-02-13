"""Module for handling Git operations."""
import subprocess
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class FileChange:
    """Represents changes in a single file."""
    filename: str
    content: str

class GitHandler:
    @staticmethod
    def get_file_changes() -> List[FileChange]:
        """Retrieves only staged changes from Git (after git add)."""
        try:
            # Get staged changes
            staged_cmd = subprocess.run(
                ['git', 'diff', '--cached', '--unified=0'],
                capture_output=True, text=True, check=True
            )
            
            if not staged_cmd.stdout:
                return []
                
            return GitHandler._parse_diff_output(staged_cmd.stdout)
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git command failed: {e.stderr}")
    
    @staticmethod
    def _parse_diff_output(diff_output: str) -> List[FileChange]:
        """Parse git diff output into FileChange objects."""
        changes = []
        diff_sections = diff_output.split('diff --git ')
        
        for section in diff_sections[1:]:  # Skip first empty section
            if not section.strip():
                continue
                
            filename = GitHandler._extract_filename(section)
            if not filename:
                continue
                
            change_content = GitHandler._extract_changes(section)
            if change_content:
                changes.append(FileChange(filename=filename, content=change_content))
                
        return changes
    
    @staticmethod
    def _extract_filename(section: str) -> Optional[str]:
        """Extract filename from diff section."""
        for line in section.split('\n'):
            if line.startswith('+++'):
                return line.split('/')[-1].strip()
        return None
    
    @staticmethod
    def _extract_changes(section: str) -> str:
        """Extract the actual changes from diff section."""
        changes = []
        for line in section.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                changes.append(f"Added: {line[1:]}")
            elif line.startswith('-') and not line.startswith('---'):
                changes.append(f"Removed: {line[1:]}")
        return "\n".join(changes)