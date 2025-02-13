"""Module for handling AI review generation."""
import click
from dataclasses import dataclass
from openai import OpenAI
from typing import List, Optional
from .git_handler import FileChange

@dataclass
class Review:
    """Represents an AI review for a file."""
    filename: str
    content: str

class AIReviewer:
    def __init__(self, model: str, api_key: str, base_url: Optional[str] = None):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url if base_url else None
        )
        self.model = model
    
    def review_changes(self, changes: List[FileChange], 
                      project_context: str, prompt_template: str) -> List[Review]:
        """Generate AI reviews for all file changes."""
        reviews = []
        for change in changes:
            click.echo(f"Generating review for {change.filename}...")
            
            review_content = self._get_review(
                change.content,
                change.filename,
                project_context,
                prompt_template
            )
            reviews.append(Review(filename=change.filename, content=review_content))
        return reviews
    
    def _get_review(self, changes: str, filename: str, 
                    project_context: str, prompt_template: str) -> str:
        """Get AI review for a single file's changes."""
        prompt = f"""{project_context}

        {prompt_template}
        
        Review the following changes in {filename}:
        ```
        {changes}
        ```
        
        Please focus your review on these specific changes."""

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                n=1,
                messages=[
                    {"role": "system", "content": "You are an experienced software engineer tasked with reviewing code changes."},
                    {"role": "user", "content": prompt},
                ]
            )
            
            return f"## Review for changes in {filename}\n\n{completion.choices[0].message.content}"
        except Exception as e:
            raise RuntimeError(f"OpenAI API error for {filename}: {str(e)}")