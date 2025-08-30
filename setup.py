#!/usr/bin/env python3
"""
Setup script for Fortune Teller package.
"""
from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if not line.startswith("#")]

# No longer generating README.md here - it already exists

setup(
    name="fortune_teller",
    version="0.1.0",
    description="基于LLM的多系统算命程序",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Fortune Teller Team",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "fortune-teller=fortune_teller.main:run_cli",
            "fortune-teller-strands=fortune_teller.strands_main:run_strands_cli",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
