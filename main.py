import sys

from app.app import start_app


def main():
    try:
        start_app()
    except ValueError as error:
        print(f"Error: {error}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)


if __name__ == "__main__":
    main()