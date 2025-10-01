from setuptools import setup, find_packages

setup(
    name="intel_harvester",
    version="0.1.0",
    description="Service for harvesting and processing simulation data.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Jules",
    package_dir={"": "services"},
    packages=find_packages(where="services"),
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
        "httpx"
    ],
    entry_points={
        "console_scripts": [
            "intel_harvester=intel_harvester.cli.main:cli",
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