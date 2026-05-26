from invoke.tasks import task


@task
def install(c):
    """Install MCP package in editable mode with dev deps."""
    c.run("pip install -e MCP/[dev]")


@task(optional=["host"], optional=["port"])
def run(c, host: str = "127.0.0.1", port: int = 8000):
    """Run the Playwright MCP server."""
    env = f"MCP_HOST={host} MCP_PORT={port}"
    c.run(f"{env} python MCP/run.py")


@task
def run_root(c):
    """Run the simple root MCP server."""
    c.run("python -m src.main")


@task
def tests(c):
    """Run pytest for the MCP subproject."""
    c.run("python -m pytest MCP/tests -v")


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
    """Run flake8 on MCP source."""
    c.run("flake8 MCP/src/")


@task
def format(c):
    """Run Black formatter on MCP source."""
    c.run("black MCP/src/ MCP/tests/")


@task(lint, format)
def lint_format(c):
    """Run linter and formatter."""
    pass
