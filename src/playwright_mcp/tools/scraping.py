"""Web scraping tool: extract content from the current page or a URL."""

import asyncio

from fastmcp import Context

from playwright_mcp.browser.state import BrowserState


async def browser_scrape(
    ctx: Context,
    url: str | None = None,
    selector: str | None = None,
    format: str = "text",
    wait_selector: str | None = None,
    wait_ms: int | None = None,
    max_length: int = 100_000,
) -> str | dict:
    """Extract content from the current page or from a URL. Use 'url' to navigate first, then scrape.
    'selector': optional CSS selector to scrape only that element (e.g. 'article', '#content').
    'format': 'text' (plain text), 'html' (raw HTML), or 'links' (list of {href, text}).
    'wait_selector': optional selector to wait for before scraping (for JS-rendered content).
    'wait_ms': optional delay in milliseconds before scraping.
    'max_length': maximum characters to return (default 100000)."""
    state: BrowserState = ctx.lifespan_context["browser_state"]
    logger = ctx.lifespan_context["logger"]
    logger.info(
        "browser_scrape",
        url=url,
        selector=selector,
        format=format,
    )
    page = state.page

    if url:
        await page.goto(url, wait_until="domcontentloaded")
    if wait_selector:
        await page.wait_for_selector(wait_selector, timeout=15_000)
    if wait_ms is not None and wait_ms > 0:
        await asyncio.sleep(wait_ms / 1000.0)

    root = page
    if selector:
        el = await page.query_selector(selector)
        if el is None:
            return f"No element found for selector: {selector}"
        root = el

    def truncate(s: str) -> str:
        if len(s) <= max_length:
            return s
        return s[:max_length] + "\n... [truncated]"

    if format == "html":
        content = await root.inner_html() if root != page else await page.content()
        return truncate(content)
    if format == "links":
        anchors = await root.query_selector_all("a[href]")
        links = []
        for a in anchors:
            href = await a.get_attribute("href") or ""
            text = (await a.inner_text()).strip()[:200]
            links.append({"href": href, "text": text})
        return {"links": links[:500]}
    # default: text
    content = await root.inner_text()
    return truncate(content)


def register_scraping_tools(mcp: object) -> None:
    """Register scraping tools with the FastMCP server."""
    mcp.add_tool(browser_scrape)
