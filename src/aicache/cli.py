import argparse
from .core import Cache

def main():
    parser = argparse.ArgumentParser(description="AI Cache CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Get command
    get_parser = subparsers.add_parser("get")
    get_parser.add_argument("prompt")
    get_parser.add_argument("--context", default=None)

    # Set command
    set_parser = subparsers.add_parser("set")
    set_parser.add_argument("prompt")
    set_parser.add_argument("response")
    set_parser.add_argument("--context", default=None)

    # List command
    list_parser = subparsers.add_parser("list")

    # Clear command
    clear_parser = subparsers.add_parser("clear")

    args = parser.parse_args()
    cache = Cache()

    if args.command == "get":
        result = cache.get(args.prompt, args.context)
        if result:
            print(result)
        else:
            print("No cache entry found.")
    elif args.command == "set":
        cache.set(args.prompt, args.response, args.context)
        print("Cache entry set.")
    elif args.command == "list":
        entries = cache.list()
        for entry in entries:
            print(entry)
    elif args.command == "clear":
        cache.clear()
        print("Cache cleared.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
