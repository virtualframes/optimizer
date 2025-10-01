"""
A parser for extracting structured data from LLM-generated text.

This module is a critical component of the synthesis layer. It takes the
semi-structured text output produced by an LLM agent and parses it into a
clean, predictable dictionary format. It uses regular expressions to robustly
extract key-value pairs and JSON-formatted data for entities like predictions
and benchmarks, making the intelligence usable by downstream systems like the
Neo4j anchor and the flaw detector.
"""
import logging
import re
import json

class PredictionParser:
    """
    Parses structured text output from an LLM synthesizer into a dictionary.
    """
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def parse(self, text_output):
        """
        Parses a block of text containing key-value pairs (e.g., `[Key]: Value`).
        """
        intelligence = {
            "title": "",
            "url": "",
            "summary": "",
            "predictions": [],
            "benchmarks": []
        }
        pattern = re.compile(r'\[([^\]]+)\]:\s*(.*?)(?=\n\[|\Z)', re.DOTALL)
        matches = pattern.findall(text_output)

        for key, value in matches:
            key = key.strip().lower()
            value = value.strip()
            try:
                if key == 'title':
                    intelligence['title'] = value
                elif key == 'url':
                    intelligence['url'] = value
                elif key == 'summary':
                    intelligence['summary'] = value
                elif key in ('prediction', 'benchmark'):
                    # Handles keys that can appear multiple times
                    intelligence[f"{key}s"].append(json.loads(value))
            except json.JSONDecodeError:
                logging.warning(f"Failed to parse JSON for key '{key}': {value}")

        return intelligence