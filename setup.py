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
        "pybullet",
        "networkx",
    ],
    extras_require={
        "dev": [
            "pytest",
            "flake8",
            "httpx",
            "temporalio",
            "openai",
            "pytest-asyncio",
            "pymilvus",
        ]
    },
    entry_points={
        "console_scripts": [
            "optimizer=optimizer.cli.main:cli",
            "graph-service=optimizer.graphs.service_graph:main",
            "graph-code=optimizer.graphs.code_graph:main",
            "graph-all=optimizer.plugins.graphs:main",
            "graph-render=optimizer.graphs.render:main",
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
