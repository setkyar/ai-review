from setuptools import setup, find_packages

# Read README.md for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aireview",
    version="1.1.0",
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