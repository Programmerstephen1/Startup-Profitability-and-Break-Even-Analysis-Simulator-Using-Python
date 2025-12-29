"""Small CLI wrapper to expose the existing `src.main` as a console entry point."""
def main():
    # Import here to keep startup fast for packaging metadata
    from src.main import main as _main

    return _main()
