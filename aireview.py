import click
import subprocess
from openai import OpenAI
import os
import configparser
import logging
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(filename='aireview.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def load_config(config_file="aireview.config"):
    """
    Loads configuration settings from the specified configuration file.
    """
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


def get_file_changes() -> List[Tuple[str, str]]:
    """
    Retrieves the staged and unstaged changes from Git.
    Returns a list of tuples containing (filename, change_content).
    Only includes the actual changes, not the entire file content.
    """
    try:
        # Get changes including staged and unstaged
        changes_cmd = subprocess.run(
            ['git', 'diff', 'HEAD', '--unified=0'],  # --unified=0 shows minimal context
            capture_output=True, text=True, check=True
        )
        
        if not changes_cmd.stdout:
            return []
            
        # Split the diff output into per-file sections
        diff_sections = changes_cmd.stdout.split('diff --git ')
        changes = []
        
        for section in diff_sections:
            if not section.strip():
                continue
                
            # Parse the filename and changes
            lines = section.split('\n')
            try:
                # Extract filename from the diff header
                file_line = next(line for line in lines if line.startswith('+++'))
                filename = file_line.split('/')[-1].strip()
                
                # Collect only the changed lines (additions and deletions)
                change_lines = []
                for line in lines:
                    if line.startswith('+') and not line.startswith('+++'):
                        change_lines.append(f"Added: {line[1:]}")
                    elif line.startswith('-') and not line.startswith('---'):
                        change_lines.append(f"Removed: {line[1:]}")
                        
                if change_lines:  # Only include files with actual changes
                    changes.append((
                        filename,
                        f"Changes in {filename}:\n" + "\n".join(change_lines)
                    ))
            except (StopIteration, IndexError):
                continue
                
        return changes
        
    except subprocess.CalledProcessError as e:
        raise Exception(f"Git command failed: {e.stderr}")


def get_ai_review(changes: str, filename: str, model: str, api_key: str, 
                  project_context: str = "", prompt_template: str = "", model_base_url: str="") -> str:
    """
    Gets the AI review for changes in a single file.
    """
    
    if model_base_url != "":
        client = OpenAI(
            api_key=api_key,
            base_url=model_base_url
        )
    else:
        client = OpenAI(api_key=api_key)
        
    prompt = f"""{project_context}

    {prompt_template}
    
    Review the following changes in {filename}:
    ```
    {changes}
    ```
    
    Please focus your review on these specific changes."""

    try:
        completion = client.chat.completions.create(
            model=model,
            n=1,
            messages=[
                {"role": "system", "content": "You are an experienced software engineer tasked with reviewing code changes."},
                {"role": "user", "content": prompt},
            ]
        )
        return f"## Review for changes in {filename}\n\n{completion.choices[0].message.content}"
    except Exception as e:
        raise Exception(f"OpenAI API error for {filename}: {e}")


def write_review_to_file(reviews: List[str], output_file: str):
    """
    Writes the AI review to file.
    """
    with open(output_file, "w") as f:
        f.write("\n\n".join(reviews))


@click.command()
@click.option('--config', default="aireview.config", help='Path to the configuration file.')
def main(config):
    """
    A CLI tool for reviewing code changes using AI, configurable via aireview.config.
    Reviews focus on the actual changes made to files, not entire file contents.
    """
    try:
        config_data = load_config(config)
        model = config_data.get("ai", "model", fallback="gpt-4")
        api_key = config_data.get("ai", "api_key", fallback="")
        base_url = config_data.get("ai", "base_url", fallback="")
        output = config_data.get("review", "output", fallback="ai-review.md")
        project_context = config_data.get("context", "project_context", fallback="")
        prompt_template = config_data.get("prompt", "prompt_template",
                                         fallback="Please review these code changes and provide specific feedback...")

        if not api_key:
            click.echo("API key is required in the configuration file.", err=True)
            logging.error("API key is required in the configuration file.")
            return

    except Exception as e:
        click.echo(f"Error loading configuration: {e}", err=True)
        logging.error(f"Error loading configuration: {e}")
        return

    try:
        file_changes = get_file_changes()
    except Exception as e:
        click.echo(f"Error getting Git changes: {e}", err=True)
        logging.error(f"Error getting Git changes: {e}")
        return

    if not file_changes:
        click.echo("No changes found. Make sure you have changes in your current directory.", err=True)
        logging.warning("No changes found.")
        return

    try:
        reviews = []
        total_files = len(file_changes)
        for i, (filename, changes) in enumerate(file_changes, 1):
            click.echo(f"Processing changes in file {i}/{total_files}: {filename}")
            review = get_ai_review(changes, filename, model, api_key, project_context, prompt_template, base_url)
            reviews.append(review)

    except Exception as e:
        click.echo(f"Error getting AI review: {e}", err=True)
        logging.error(f"Error getting AI review: {e}")
        return

    try:
        write_review_to_file(reviews, output)
        click.echo(f"AI review written to {output}")
        logging.info(f"AI review written to {output}")
    except Exception as e:
        click.echo(f"Error writing review to file: {e}", err=True)
        logging.error(f"Error writing review to file: {e}")
        return


if __name__ == '__main__':
    main()