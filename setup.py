from setuptools import setup, find_packages

setup(
    name="solvedesk",
    version="1.0.0",

    packages=find_packages(),

    install_requires=[
        "typer",
        "rich"
    ],

    entry_points={
        "console_scripts": [
            "solvedesk=solvedesk_cmd.cmd:app"
        ]
    }
)