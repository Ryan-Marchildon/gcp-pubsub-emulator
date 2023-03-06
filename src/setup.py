from setuptools import setup, find_packages

setup(
    name="pubsub-demo",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": ["stamps=pubsub_demo.cli:main"],
    },
)
