from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="optimizer",
    version="0.1.0",
    author="VirtualFrames",
    description="Augmented optimizer for virtual node and game-engine authentication matrix simulation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/virtualframes/optimizer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pybullet>=3.2.0",
        "numpy>=1.21.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "optimizer=optimizer.cli:main",
        ],
    },
)
