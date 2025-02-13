"""Module for handling configuration management."""
import configparser
import logging
from dataclasses import dataclass
from typing import Optional, Tuple, Union
from typing_extensions import Literal

@dataclass
class AIConfig:
    """Configuration settings for AI service."""
    model: str
    api_key: str
    base_url: Optional[str] = None

@dataclass
class ReviewConfig:
    """Configuration settings for review output."""
    output_file: str
    project_context: str
    prompt_template: str

class ConfigLoader:
    def __init__(self, config_file: str = "aireview.config"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        
    def load(self) -> Tuple[AIConfig, ReviewConfig]:
        """Load and validate configuration settings."""
        self.config.read(self.config_file)
        
        ai_config = AIConfig(
            model=self.config.get("ai", "model", fallback="gpt-4"),
            api_key=self.config.get("ai", "api_key", fallback=""),
            base_url=self.config.get("ai", "base_url", fallback="")
        )
        
        if not ai_config.api_key:
            raise ValueError("API key is required in the configuration file.")
            
        review_config = ReviewConfig(
            output_file=self.config.get("review", "output", fallback="ai-review.md"),
            project_context=self.config.get("context", "project_context", fallback=""),
            prompt_template=self.config.get("prompt", "prompt_template",
                fallback="Please review these code changes and provide specific feedback...")
        )
        
        return ai_config, review_config