# Playwright MCP

FastMCP server with Playwright for browser automation and web scraping. Exposes tools over HTTP for use with MCP clients (e.g. GPT-based agents).

## Features

- **HTTP transport** – Server runs as an HTTP service; clients connect via URL.
- **Long-lived browser** – One Chromium instance started at server startup (Option A).
- **Structured logging** – Structlog with configurable level and JSON output.
- **Modular layout** – Config, logging, browser, tools, and server are separate; state is injected via lifespan context.

## Tools

| Tool | Description |
|------|-------------|
| `browser_navigate` | Navigate to a URL |
| `browser_snapshot` | Get HTML/text snapshot of the current page |
| `browser_tabs` | List open tabs (pages) |
| `browser_click` | Click an element by CSS selector |
| `browser_type` | Type text into an element |
| `browser_fill_form` | Fill multiple form fields (selector → value map) |
| `browser_scrape` | Extract content (text, HTML, or links) from current page or URL |
| `browser_screenshot` | Take a PNG screenshot (base64) of page or element |

## Requirements

- Python 3.10+
- Playwright browsers (install after `pip install`)

## Setup

```bash
# From project root
pip install -e .
python -m playwright install chromium
```

Optional: copy `.env.example` to `.env` and adjust `MCP_HOST`, `MCP_PORT`, `HEADLESS`, `LOG_LEVEL`, `LOG_JSON`.

## Run

```bash
# After pip install -e .
playwright-mcp

# Or
python -m playwright_mcp.main
```

Server listens at `http://127.0.0.1:8000` by default. MCP endpoint is typically at `http://127.0.0.1:8000/mcp` (see FastMCP HTTP deployment docs).

## Project layout

```
src/playwright_mcp/
├── main.py           # Entrypoint
├── config/           # Env-based settings
├── logging_/          # Structlog setup and get_logger
├── browser/          # Lifecycle and BrowserState
├── tools/            # Navigation, interaction, scraping, screenshot
└── server/           # FastMCP app and dependency registration
```

## Configuration

| Env var | Default | Description |
|---------|---------|-------------|
| `MCP_HOST` | `127.0.0.1` | HTTP bind host |
| `MCP_PORT` | `8000` | HTTP bind port |
| `HEADLESS` | `true` | Run browser headless |
| `LOG_LEVEL` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_JSON` | `false` | Output logs as JSON |
