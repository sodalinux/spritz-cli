from importlib_metadata import entry_points
from setuptools import setup

setup(
    name="spritz-cli",
    version="1.0",
    py_modules=['spritz'],
    install_requires=['typer', 'tqdm'],
    entry_points="""
        [console_scripts]
        spritz=spritz:app
    """



)