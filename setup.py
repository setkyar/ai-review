from setuptools import setup, find_packages
import os
import subprocess

def get_version_from_git():
    """Get version from git tags."""
    try:
        # Get the latest git tag
        process = subprocess.Popen(['git', 'describe', '--tags', '--abbrev=0'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        version, stderr = process.communicate()
        
        if process.returncode != 0:
            # If no tags exist, start with 0.1.0
            return '0.1.0'
            
        # Convert bytes to string and strip whitespace
        version = version.decode('utf-8').strip()
        
        # Remove 'v' prefix if it exists
        if version.startswith('v'):
            version = version[1:]
            
        return version
    except Exception:
        # Fallback version if git is not available
        return '0.1.0'

# Get version from git tags
version = get_version_from_git()

# Read README.md for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aireview",
    version=version,
    author="Set Kyar Wa Lar",
    author_email="me@setkyar.com",
    description="AI-powered code review tool for Git repositories",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/setkyar/aireview",
    project_urls={
        "Bug Tracker": "https://github.com/setkyar/aireview/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "click>=8.1.8",
        "openai>=1.62.0",
        "configparser>=7.1.0",
        "typing-extensions>=4.0.0",  # For Python 3.8 compatibility
    ],
    entry_points={
        'console_scripts': [
            'aireview=aireview.main:main',
        ],
    },
    extras_require={
        'test': [
            'pytest>=7.0.0,<8.0.0',
            'pytest-cov>=4.1.0,<5.0.0',
            'pytest-mock>=3.10.0',
        ],
    },
)