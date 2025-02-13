"""Module for handling AI review generation."""
import click
import asyncio
from dataclasses import dataclass
from openai import AsyncOpenAI
from typing import List, Optional
from .git_handler import FileChange

@dataclass
class Review:
    """Represents an AI review for a file."""
    filename: str
    content: str

class AIReviewer:
    def __init__(self, model: str, api_key: str, base_url: Optional[str] = None):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url if base_url else None
        )
        self.model = model
    
    async def review_changes(self, changes: List[FileChange], 
                           project_context: str, prompt_template: str) -> List[Review]:
        """Generate AI reviews for all file changes in parallel."""
        click.echo(f"Generating reviews for {len(changes)} files...")
        
        # Create tasks for all reviews
        tasks = []
        for change in changes:
            click.echo(f"Starting review for {change.filename}...")
            
            # Create prompt with filename included
            prompt = self._create_prompt(
                changes=change.content,
                filename=change.filename,
                file_content=change.file_content,
                project_context=project_context,
                prompt_template=prompt_template
            )
            
            # Create task for this review
            tasks.append(self._get_review(prompt, change.filename))
        
        # Run all reviews concurrently
        review_contents = await asyncio.gather(*tasks)
        
        # Create Review objects from results
        reviews = [
            Review(filename=changes[i].filename, content=content)
            for i, content in enumerate(review_contents)
        ]
        
        return reviews
    
    def _create_prompt(self, changes: str, filename: str,
                      file_content: Optional[str], project_context: str,
                      prompt_template: str) -> str:
        """Create the prompt for a single file review."""
        # Include file content in the prompt if available
        file_content_section = ""
        if file_content:
            file_content_section = f"""
            Current file content:
            ```
            {file_content}
            ```
            """

        return f"""{project_context}

        {prompt_template}
        
        Review the following changes in {filename}:
        ```
        {changes}
        ```
        {file_content_section}
        Please focus your review on these specific changes."""
    
    async def _get_review(self, prompt: str, filename: str) -> str:
        """Get AI review for the provided prompt."""
        try:
            completion = await self.client.chat.completions.create(
                model=self.model,
                n=1,
                messages=[
                    {"role": "system", "content": "You are an experienced software engineer tasked with reviewing code changes."},
                    {"role": "user", "content": prompt},
                ]
            )
            
            click.echo(f"Completed review for {filename}")
            return f"## Review for changes in {filename}\n\n{completion.choices[0].message.content}"
        except Exception as e:
            raise RuntimeError(f"OpenAI API error for {filename}: {str(e)}")