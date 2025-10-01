def synthesize_patch(diagnosis: str) -> dict:
    if "g++" in diagnosis:
        return {
            "file": "Dockerfile",
            "insert": "RUN apt-get update && apt-get install -y build-essential"
        }
    return {}