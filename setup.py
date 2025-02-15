from setuptools import setup, find_packages

setup(
    name='ghook',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ghook = ghook.cli:main',
        ],
    },
    install_requires=[],
)
