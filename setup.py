from setuptools import setup

setup(
    name='aireview',
    version='0.1.0',
    py_modules=['aireview'],
    install_requires=[
        'click',
        'openai',
    ],
    entry_points={
        'console_scripts': [
            'aireview = aireview:main',
        ],
    },
)