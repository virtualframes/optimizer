import typer
from optimizer.cli import vm

app = typer.Typer(
    name="jules",
    help="Jules Mission Ω - The mutation-aware agentic orchestration platform.",
    no_args_is_help=True,
)

# Add the new command group
app.add_typer(vm.app)

@app.command()
def run():
    """A placeholder for the main 'jules-run-agent' command."""
    print("Running main agent... (to be implemented)")

if __name__ == "__main__":
    app()