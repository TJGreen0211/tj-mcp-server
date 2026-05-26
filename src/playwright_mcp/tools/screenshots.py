"""Screenshot tool: capture the current page or an element as PNG."""

import base64

from fastmcp import Context

from playwright_mcp.browser.state import BrowserState


async def browser_screenshot(
    ctx: Context,
    selector: str | None = None,
    full_page: bool = False,
) -> str:
    """Take a screenshot of the current page. Returns base64-encoded PNG.
    Use 'selector' to capture only that element, or set 'full_page' to True for the full scrollable page."""
    state: BrowserState = ctx.lifespan_context["browser_state"]
    logger = ctx.lifespan_context["logger"]
    logger.info("browser_screenshot", selector=selector, full_page=full_page)
    page = state.page

    if selector:
        element = await page.query_selector(selector)
        if element is None:
            return f"Error: no element found for selector {selector}"
        png_bytes = await element.screenshot(type="png")
    else:
        png_bytes = await page.screenshot(type="png", full_page=full_page)

    return base64.b64encode(png_bytes).decode("ascii")


def register_screenshot_tools(mcp: object) -> None:
    """Register screenshot tools with the FastMCP server."""
    mcp.add_tool(browser_screenshot)
