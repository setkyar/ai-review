# AIReview

[![PyPI](https://img.shields.io/pypi/v/aireview.svg)](https://pypi.org/project/aireview/)
[![Changelog](https://img.shields.io/github/v/release/setkyar/ai-review?include_prereleases&label=changelog)](https://github.com/setkyar/ai-review/releases)
[![Tests](https://github.com/setkyar/ai-review/actions/workflows/test.yml/badge.svg)](https://github.com/setkyar/ai-review/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/setkyar/ai-review/graph/badge.svg?token=RNWN1A9D8J)](https://codecov.io/gh/setkyar/ai-review)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/setkyar/ai-review/blob/master/LICENSE)

AIReview is a command-line tool that leverages LLM to provide code reviews for your Git changes.

## Features

- Automatic detection of Git changes
- AI-powered code review using OpenAI's GPT models
- Customizable review prompts and project context
- Markdown-formatted review output
- Support for multiple file reviews in a single run

## Installation

1. Clone the repository:
```bash
git clone https://github.com/setkyar/aireview.git
cd aireview
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package:
```bash
pip install -e .
```

## Configuration

Create a configuration file named `aireview.config` with the following structure:

```ini
[ai]
model = gpt-4
api_key = your_openai_api_key
base_url = https://api.openai.com/v1  # Optional: for custom OpenAI-compatible endpoints

[review]
output = ai-review.md # Output file for the review comments

[context]
project_context = Your project context description... # Example, I am working on Nodejs, typescript project

[prompt]
prompt_template = Your custom review prompt... # Example, Review the changes and provide feedback on the code quality and best practices
```

## Usage

1. Make some changes in your Git repository
2. Add changes to the staging area:
```bash
git add  the/changed/files
```
3. Run AIReview:
```bash
aireview --config path/to/aireview.config
```

The tool will:
1. Detect your Git changes
2. Send them to the LLM for review
3. Generate a markdown file with the review comments

## Development

### Running Tests

```bash
# Install test dependencies
pip install -e ".[test]"

# Run tests
pytest

# Run tests with coverage
coverage run -m pytest
coverage report
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request