from setuptools import setup, find_packages

# Read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read the contents of your requirements file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="syzygy-synapse",
    version="0.1.0",
    description="A multi-agent, self-healing software development framework.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Jules",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "syzygy=flaw_first_optimizer.psi_kernel:main",
            "jules-worker=jules.worker:main",
            "jules-trigger=jules.workflow:main",
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