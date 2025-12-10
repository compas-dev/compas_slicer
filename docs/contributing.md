# Contributing

We welcome contributions to COMPAS Slicer!

## Development Setup

1. Fork and clone the repository:

    ```bash
    git clone https://github.com/YOUR_USERNAME/compas_slicer.git
    cd compas_slicer
    ```

2. Install in development mode:

    ```bash
    pip install -e ".[dev]"
    ```

3. Verify tests pass:

    ```bash
    pytest
    ```

## Code Style

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
# Check for issues
ruff check src/

# Auto-fix issues
ruff check --fix src/

# Format code
ruff format src/
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=compas_slicer

# Run specific test file
pytest tests/test_planar_slicing.py
```

## Pull Request Process

1. Create a feature branch from `master`
2. Make your changes
3. Ensure tests pass and code is formatted
4. Add yourself to the authors in `pyproject.toml` if not already listed
5. Create a pull request with a clear description

## Adding Examples

When adding new functionality:

1. Add an example in `examples/` demonstrating the feature
2. Ensure the example runs without errors
3. Add documentation if needed

## Documentation

Build the docs locally:

```bash
pip install -e ".[docs]"
mkdocs serve
```

Then open http://localhost:8000 in your browser.

## Releasing

Maintainers can release new versions:

```bash
# Bump version (patch/minor/major)
bump2version patch

# Push with tags
git push && git push --tags
```

## Questions?

- Open an [issue](https://github.com/compas-dev/compas_slicer/issues)
- Contact the maintainers
