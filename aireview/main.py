"""Main module for the AI code review tool."""
import click
import logging
from typing import List
from .config import ConfigLoader
from .git_handler import GitHandler
from .ai_reviewer import AIReviewer, Review

def setup_logging():
    """Configure logging settings."""
    logging.basicConfig(
        filename='aireview.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def write_reviews(reviews: List[Review], output_file: str):
    """Write reviews to output file."""
    content = "\n\n".join(review.content for review in reviews)
    with open(output_file, "w") as f:
        f.write(content)

@click.command()
@click.option('--config', default="aireview.config", help='Path to the configuration file.')
def main(config: str):
    """AI-powered code review tool."""
    setup_logging()
    
    try:
        # Load configuration
        config_loader = ConfigLoader(config)
        ai_config, review_config = config_loader.load()
        
        # Get git changes
        git_handler = GitHandler()
        file_changes = git_handler.get_file_changes()
        
        if not file_changes:
            click.echo("No changes found. Make sure you have changes in your current directory.")
            logging.warning("No changes found.")
            return
        
        # Generate reviews
        reviewer = AIReviewer(
            model=ai_config.model,
            api_key=ai_config.api_key,
            base_url=ai_config.base_url
        )
        
        reviews = reviewer.review_changes(
            file_changes,
            review_config.project_context,
            review_config.prompt_template
        )
        
        # Write output
        write_reviews(reviews, review_config.output_file)
        click.echo(f"AI review written to {review_config.output_file}")
        logging.info(f"AI review written to {review_config.output_file}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        logging.error(f"Error: {str(e)}")
        return