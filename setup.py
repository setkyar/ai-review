from setuptools import setup, find_packages

setup(
    name="aireview",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click",
        "openai",
        "configparser",
    ],
    entry_points={
        'console_scripts': [
            'aireview=aireview.main:main',
        ],
    },
    python_requires=">=3.7",
    description="An AI-powered code review tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/setkyar/aireview",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)