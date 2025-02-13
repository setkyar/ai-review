"""Module for handling Git operations."""
import subprocess
from dataclasses import dataclass
from typing import List, Optional, Dict
import os

@dataclass
class FileChange:
    """Represents changes in a single file."""
    filename: str
    content: str
    file_content: Optional[str] = None

class GitHandler:
    @staticmethod
    def get_file_changes() -> List[FileChange]:
        """Retrieves staged changes from Git and their corresponding file content efficiently."""
        try:
            # Get staged changes
            staged_cmd = subprocess.run(
                ['git', 'diff', '--cached', '--unified=0'],
                capture_output=True, text=True, check=True
            )
            
            if not staged_cmd.stdout:
                return []
            
            # Parse the diff output first
            changes = GitHandler._parse_diff_output(staged_cmd.stdout)
            
            # Get the list of files we need content for
            files_to_fetch = [change.filename for change in changes]
            
            # Batch fetch file contents
            file_contents = GitHandler._batch_get_file_contents(files_to_fetch)
            
            # Update FileChange objects with their content
            for change in changes:
                change.file_content = file_contents.get(change.filename)
            
            return changes
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git command failed: {e.stderr}")
    
    @staticmethod
    def _batch_get_file_contents(filenames: List[str]) -> Dict[str, Optional[str]]:
        """
        Efficiently get contents of multiple files using git cat-file --batch.
        Returns a dictionary mapping filenames to their content.
        """
        if not filenames:
            return {}
        
        try:
            # Get object IDs for staged versions of files
            file_revs = {}
            for filename in filenames:
                try:
                    rev_cmd = subprocess.run(
                        ['git', 'rev-parse', f':"{filename}"'],
                        capture_output=True, text=True, check=True
                    )
                    file_revs[filename] = rev_cmd.stdout.strip()
                except subprocess.CalledProcessError:
                    # File might be new/deleted
                    file_revs[filename] = None
            
            # Prepare batch input
            valid_revs = {f: rev for f, rev in file_revs.items() if rev is not None}
            if not valid_revs:
                return {f: None for f in filenames}
            
            # Start git cat-file --batch process
            process = subprocess.Popen(
                ['git', 'cat-file', '--batch'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Write object IDs to git cat-file
            input_data = '\n'.join(valid_revs.values()) + '\n'
            stdout, stderr = process.communicate(input_data.encode())
            
            if process.returncode != 0:
                raise subprocess.CalledProcessError(
                    process.returncode, 'git cat-file', stderr
                )
            
            # Parse the output
            contents = {}
            current_content = []
            current_file = None
            rev_to_file = {rev: f for f, rev in valid_revs.items()}
            
            for line in stdout.decode().split('\n'):
                if line.strip() and ' blob ' in line:
                    # New blob header - save previous content if any
                    if current_file and current_content:
                        contents[current_file] = ''.join(current_content)
                        current_content = []
                    
                    # Get filename for this blob
                    obj_id = line.split()[0]
                    current_file = rev_to_file.get(obj_id)
                else:
                    current_content.append(line + '\n')
            
            # Save last file's content
            if current_file and current_content:
                contents[current_file] = ''.join(current_content)
            
            # Include None for files that weren't found
            return {f: contents.get(f) for f in filenames}
            
        except Exception as e:
            # If batch operation fails, fall back to individual git show commands
            return GitHandler._fallback_get_file_contents(filenames)
    
    @staticmethod
    def _fallback_get_file_contents(filenames: List[str]) -> Dict[str, Optional[str]]:
        """Fallback method to get file contents using git show."""
        contents = {}
        for filename in filenames:
            try:
                show_cmd = subprocess.run(
                    ['git', 'show', f':{filename}'],
                    capture_output=True, text=True, check=True
                )
                contents[filename] = show_cmd.stdout
            except subprocess.CalledProcessError:
                contents[filename] = None
        return contents
    
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