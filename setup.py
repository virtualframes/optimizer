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
        "pathspec>=0.12.1",
        "requests>=2.32",
        "beautifulsoup4>=4.12"
    ],
    extras_require={
        "atlas": ["PyYAML>=6.0.2", "pathspec>=0.12.1", "requests>=2.32", "beautifulsoup4>=4.12"],
    },
    entry_points={
        "console_scripts": [
            "optimizer=optimizer.cli.main:cli",
            "map-tree=optimizer.research.tree_mapper:main",
            "api-map=optimizer.apiatlas.cli:map_main",
            "api-health=optimizer.apiatlas.cli:health_main",
            "api-heal=optimizer.apiatlas.cli:heal_main",
            "api-debug=optimizer.apiatlas.cli:debug_main",
            "omega-inject=optimizer.resilience.entropy:main",
            "omega-stress=optimizer.benchmark.availability_stress:main",
            "jules-index-context=optimizer.context_engine.spacetime_indexer:main",
            "jules-retrieve-context=optimizer.context_engine.context_retriever:main",
            "lineage-render=optimizer.dev.mermaid_lineage:main",
            "service-graph=optimizer.dev.service_graph:main",
            "jules-retrieval-flow=optimizer.dev.retrieval_flow:main",
            "agentic-api-dev=optimizer.agentic_api.run:main",
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
