"""
This module is responsible for creating a unique, deterministic fingerprint
for any given piece of data (prompt, source code, etc.). This fingerprint
is the core of the system's auditability, allowing every action and mutation
to be traced back to its origin.
"""
import hashlib

def fingerprint_prompt(prompt):
    """
    Creates a SHA256 hash of a prompt to serve as a unique fingerprint.
    """
    return hashlib.sha256(prompt.encode()).hexdigest()