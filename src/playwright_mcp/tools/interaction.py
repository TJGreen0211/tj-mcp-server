"""Interaction tools: click, type, fill."""

from fastmcp import Context

from playwright_mcp.browser.state import BrowserState


async def browser_click(ctx: Context, selector: str) -> str:
    """Click an element on the page. Provide a CSS selector (e.g. 'button.submit', '#login')."""
    state: BrowserState = ctx.lifespan_context["browser_state"]
    logger = ctx.lifespan_context["logger"]
    logger.info("browser_click", selector=selector)
    page = state.page
    await page.click(selector, timeout=10_000)
    return f"Clicked: {selector}"


async def browser_type(ctx: Context, selector: str, text: str) -> str:
    """Type text into an element. Use a CSS selector to target the input/textarea."""
    state: BrowserState = ctx.lifespan_context["browser_state"]
    logger = ctx.lifespan_context["logger"]
    logger.info("browser_type", selector=selector)
    page = state.page
    await page.fill(selector, text)
    return f"Typed into {selector}"


async def browser_fill_form(
    ctx: Context,
    fields: dict[str, str],
) -> str:
    """Fill multiple form fields at once. Pass a JSON object mapping CSS selectors to values, e.g. {\"#email\": \"user@example.com\", \"#password\": \"secret\"}."""
    state: BrowserState = ctx.lifespan_context["browser_state"]
    logger = ctx.lifespan_context["logger"]
    logger.info("browser_fill_form", keys=list(fields.keys()))
    page = state.page
    for selector, value in fields.items():
        await page.fill(selector, value)
    return f"Filled {len(fields)} field(s)"


def register_interaction_tools(mcp: object) -> None:
    """Register interaction tools with the FastMCP server."""
    mcp.add_tool(browser_click)
    mcp.add_tool(browser_type)
    mcp.add_tool(browser_fill_form)
