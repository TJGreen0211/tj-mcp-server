"""Navigation tools: goto, snapshot, tabs."""

from fastmcp import Context

from playwright_mcp.browser.state import BrowserState


async def browser_navigate(ctx: Context, url: str) -> str:
    """Navigate the browser to a URL. Use this to open or change the current page."""
    state: BrowserState = ctx.lifespan_context["browser_state"]
    logger = ctx.lifespan_context["logger"]
    logger.info("browser_navigate", url=url)
    page = state.page
    response = await page.goto(url, wait_until="domcontentloaded")
    if response is None:
        return "Navigation initiated (no response)."
    status = response.status
    status_text = response.status_text
    return f"Navigated to {url}. Status: {status} {status_text}"


async def browser_snapshot(ctx: Context) -> str:
    """Get a text snapshot of the current page (accessibility tree / main content) for understanding layout and elements."""
    state: BrowserState = ctx.lifespan_context["browser_state"]
    logger = ctx.lifespan_context["logger"]
    logger.info("browser_snapshot")
    page = state.page
    try:
        content = await page.content()
        body_start = content.find("<body")
        if body_start != -1:
            content = content[body_start:]
        if len(content) > 50_000:
            content = content[:50_000] + "\n... [truncated]"
        return content
    except Exception as e:
        logger.exception("browser_snapshot failed")
        return f"Error getting snapshot: {e!s}"


async def browser_tabs(ctx: Context) -> list[dict]:
    """List open browser tabs (pages) in the current context."""
    state: BrowserState = ctx.lifespan_context["browser_state"]
    logger = ctx.lifespan_context["logger"]
    logger.info("browser_tabs")
    context = state.context
    pages = context.pages
    return [
        {"index": i, "url": await p.url(), "title": await p.title()}
        for i, p in enumerate(pages)
    ]


def register_navigation_tools(mcp: object) -> None:
    """Register navigation tools with the FastMCP server."""
    mcp.add_tool(browser_navigate)
    mcp.add_tool(browser_snapshot)
    mcp.add_tool(browser_tabs)
