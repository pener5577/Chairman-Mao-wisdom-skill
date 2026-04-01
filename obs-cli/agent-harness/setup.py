#!/usr/bin/env python3
"""
setup.py for obs-cli

OBS Studio CLI - Control OBS via command line

Install with: pip install -e .
"""

from setuptools import setup, find_packages

setup(
    name="obs-cli",
    version="1.0.0",
    author="OpenClaw",
    author_email="",
    description="OBS Studio CLI - A stateful command-line interface for OBS Studio",
    long_description="OBS Studio CLI provides full OBS control via WebSocket or simulation mode.",
    long_description_content_type="text/markdown",
    url="https://github.com/openclaw/obs-cli",
    packages=find_packages(include=["cli_anything.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Video :: Capture",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0.0",
        "websocket-client>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "obs-cli=cli_anything.obs_studio.obs_studio_cli:main",
        ],
    },
    package_data={
        "cli_anything.obs_studio": ["skills/*.md"],
    },
    include_package_data=True,
    zip_safe=False,
)
