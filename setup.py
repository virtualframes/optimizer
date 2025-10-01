from setuptools import setup, find_packages

setup(
    name="optimizer",
    version="0.1.0",
    description="Augmented optimizer for virtual node and game-engine authentication matrix simulation.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Jules",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn[standard]",
        "pydantic",
        "pyyaml",
        "click",
        "pytest",
        "flake8",
        "pybullet",
        "networkx",
    ],
    entry_points={
        "console_scripts": [
            "optimizer=optimizer.cli.main:cli",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
)
