def command(name):
    """A dummy decorator to match the user's code structure."""
    def decorator(func):
        return func
    return decorator