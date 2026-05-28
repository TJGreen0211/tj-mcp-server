from invoke.tasks import task


@task
def install(c):
    """Install package in editable mode with dev deps."""
    c.run("pip install -e .[dev]")


@task(optional=["host", "port"])
def run_playwright(c, host: str = "0.0.0.0", port: int = 9000):
    """Run the Playwright MCP server."""
    c.run(
        "python -m playwright_mcp.main",
        env={
            "PYTHONPATH": "src",
            "MCP_HOST": host,
            "MCP_PORT": str(port),
        },
    )


@task(optional=["host", "port"])
def run_memory(c, host: str = "0.0.0.0", port: int = 9001):
    """Run the Memory MCP server."""
    c.run(
        "python -m memory.main",
        env={
            "PYTHONPATH": "src",
            "MCP_HOST": host,
            "MCP_PORT": str(port),
        },
    )


@task(optional=["host", "port"])
def run_sqlite(c, host: str = "0.0.0.0", port: int = 9002):
    """Run the SQLite MCP server."""
    c.run(
        "python -m sqlite.main",
        env={
            "PYTHONPATH": "src",
            "MCP_HOST": host,
            "MCP_PORT": str(port),
        },
    )


@task
def playwright_install(c):
    """Install Playwright browsers."""
    c.run("playwright install")


@task(playwright_install)
def setup(c):
    """Full setup: install package and Playwright browsers."""
    install(c)


@task
def lint(c):
    """Run flake8 on source."""
    c.run("flake8 src/")


@task
def format(c):
    """Run Black formatter on source."""
    c.run("black src/")


@task(lint, format)
def lint_format(c):
    """Run linter and formatter."""
    pass
