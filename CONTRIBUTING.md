# Contributing to aicache

We welcome contributions to `aicache`! Your help is invaluable in making this tool better.

## How to Contribute

There are several ways to contribute:

*   **Report Bugs:** If you find a bug, please open an issue on our GitHub repository. Provide a clear description, steps to reproduce, and expected behavior.
*   **Suggest Features:** Have an idea for a new feature or improvement? Open an issue to discuss it.
*   **Contribute Code:** If you'd like to contribute code, please follow the guidelines below.

## Development Setup

To set up your development environment:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/asmeyatsky/aicache.git
    cd aicache
    ```

2.  **Install dependencies and set up wrappers:**
    ```bash
    make setup
    ```
    This command will create a virtual environment, install all necessary Python dependencies, and set up the CLI wrappers in your `~/.local/bin` directory.

3.  **Activate the virtual environment:**
    ```bash
    source venv/bin/activate
    ```
    You should activate the virtual environment in each new terminal session where you plan to develop.

## Running Tests

Before submitting a pull request, please ensure all tests pass:

```bash
make test
```
This command will run all unit tests. Please add new tests for any new features or bug fixes.

## Code Style and Quality

*   **Python:** Adhere to [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines. We recommend using a linter like `flake8` or `ruff` to check your code.
*   **Shell Scripts:** Follow common shell scripting best practices.

## Pull Request Process

1.  **Fork the repository** and create your branch from `main`.
2.  **Make your changes.**
3.  **Write clear, concise commit messages.** We follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification (e.g., `feat: add new feature`, `fix: resolve bug`).
4.  **Ensure your code passes all tests** (`make test`).
5.  **Update documentation** (e.g., `README.md`, `roadmap.md`) if your changes affect user-facing features or project direction.
6.  **Submit a Pull Request.** Provide a clear description of your changes and reference any related issues.

We appreciate your contributions!