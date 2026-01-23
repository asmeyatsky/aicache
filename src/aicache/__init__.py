# AI Cache - Stop paying for duplicate AI queries

__version__ = "0.1.0"

# Try to import modern CLI first
try:
    from .modern_cli import main
except ImportError:
    # Fallback to legacy CLI
    try:
        from .cli import main
    except ImportError:
        # Basic fallback
        def main():
            print("AI Cache CLI not available. Please install with: pip install aicache[basic]")
