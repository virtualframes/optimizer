"""
Configuration for SentinelCore.
"""

class Config:
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "password"

    REDIS_HOST = "localhost"
    REDIS_PORT = 6379

config = Config()