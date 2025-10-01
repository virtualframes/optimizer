"""Setup configuration for optimizer package."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="optimizer",
    version="0.1.0",
    author="VirtualFrames",
    description="Augmented optimizer for virtual node and game engine authentication matrix simulation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/virtualframes/optimizer",
    packages=find_packages(exclude=["tests*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "optimizer=optimizer.cli:main",
        ],
    },
)
