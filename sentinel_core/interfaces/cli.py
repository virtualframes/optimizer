"""
CLI for SentinelCore.
"""

import typer

app = typer.Typer()

@app.command()
def monitor():
    """Placeholder for monitoring from the CLI."""
    print("Monitoring for signals...")

if __name__ == "__main__":
    app()