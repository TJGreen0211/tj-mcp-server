"""Web scraping tool: extract content from the current page or a URL."""

import asyncio

from fastmcp import Context

from playwright_mcp.browser.state import BrowserState

# Elements to hide when stripping boilerplate
BOILERPLATE_SELECTORS = ",".join([
    "nav", "footer", "header", "aside", "noscript", "script", "style",
    "[role=navigation]", "[role=complementary]", "[role=presentation]",
    ".sidebar", ".nav", ".navigation", ".menu", ".footer", ".header",
    ".cookie-banner", ".cookie-notice", ".popup", ".modal-overlay",
    ".ads", ".advertisement", ".banner", ".social-share", ".social-media",
    ".related-posts", ".newsletter", ".subscribe", ".breadcrumb",
])

# Primary content selectors, tried in order
MAIN_CONTENT_SELECTORS = [
    "article", "main", "[role=main]", "#content", "#main",
    ".post-content", ".article-body", ".entry-content", ".content",
]


def _accessibility_tree_to_text(node: dict, indent: int = 0) -> list[str]:
    """Convert an accessibility tree node into compact markdown-like text."""
    lines: list[str] = []
    role = node.get("role", "")
    name = (node.get("name") or "").strip()
    value = (node.get("value") or "").strip()
    description = (node.get("description") or "").strip()
    children = node.get("children") or []

    prefix = "  " * indent

    # Skip purely presentational nodes with no content
    if role == "generic" and not name and not value and not children:
        return lines
    if role == "text" and not name:
        return lines

    # Build the line for this node
    parts: list[str] = []
    if role and role != "generic":
        parts.append(f"[{role}]")
    if name:
        parts.append(name)
    elif value:
        parts.append(value)
    elif description:
        parts.append(f"({description})")

    if parts:
        lines.append(f"{prefix}{' '.join(parts)}")

    # Recurse into children
    for child in children:
        lines.extend(_accessibility_tree_to_text(child, indent + 1 if role != "generic" else indent))

    return lines


async def _hide_boilerplate(page) -> None:
    """Hide common boilerplate elements via display:none."""
    await page.evaluate(f"""() => {{
        document.querySelectorAll('{BOILERPLATE_SELECTORS}').forEach(el => {{
            el.style.display = 'none';
        }});
    }}""")


async def _restore_boilerplate(page) -> None:
    """Restore boilerplate elements by removing inline display:none."""
    await page.evaluate(f"""() => {{
        document.querySelectorAll('{BOILERPLATE_SELECTORS}').forEach(el => {{
            el.style.display = '';
        }});
    }}""")


async def _extract_main_content(page) -> tuple:
    """Try to find the main content element. Returns (element, selector_used)."""
    for sel in MAIN_CONTENT_SELECTORS:
        el = await page.query_selector(sel)
        if el:
            text = await el.inner_text()
            if len(text.strip()) > 50:
                return (el, sel)
    return (None, None)


async def browser_scrape(
    ctx: Context,
    url: str | None = None,
    selector: str | None = None,
    mode: str = "text",
    wait_selector: str | None = None,
    wait_ms: int | None = None,
    max_length: int = 20_000,
) -> str | dict:
    """Extract content from the current page or from a URL. Use 'url' to navigate first, then scrape.

    'selector': optional CSS selector to scrape only that element (e.g. 'article', '#content').
    'mode': content extraction mode:
      - 'text': full page text (legacy behavior)
      - 'main': target only the main content area, boilerplate stripped
      - 'accessible': use the accessibility tree for clean, structured output
      - 'headings': extract just the heading hierarchy for a quick overview
    'wait_selector': optional selector to wait for before scraping (for JS-rendered content).
    'wait_ms': optional delay in milliseconds before scraping.
    'max_length': maximum characters to return (default 20000)."""
    state: BrowserState = ctx.lifespan_context["browser_state"]
    logger = ctx.lifespan_context["logger"]
    logger.info(
        "browser_scrape",
        url=url,
        selector=selector,
        mode=mode,
    )
    page = state.page

    if url:
        await page.goto(url, wait_until="domcontentloaded")
    if wait_selector:
        await page.wait_for_selector(wait_selector, timeout=15_000)
    if wait_ms is not None and wait_ms > 0:
        await asyncio.sleep(wait_ms / 1000.0)

    def truncate(s: str) -> str:
        if len(s) <= max_length:
            return s
        return s[:max_length] + "\n... [truncated]"

    # --- accessible mode: use accessibility tree ---
    if mode == "accessible":
        if selector:
            el = await page.query_selector(selector)
            if el is None:
                return f"No element found for selector: {selector}"
            # Highlight the target element so accessibility snapshot focuses on it
            await el.evaluate("(el) => el.setAttribute('aria-label', '__TARGET__')")
            snapshot = await page.accessibility.snapshot(interesting_only=True)
            await el.evaluate("(el) => el.removeAttribute('aria-label')")
        else:
            snapshot = await page.accessibility.snapshot(interesting_only=True)

        lines = _accessibility_tree_to_text(snapshot)
        result = "\n".join(line for line in lines if line.strip())
        return truncate(result)

    # --- headings mode ---
    if mode == "headings":
        if selector:
            root_el = await page.query_selector(selector)
            if root_el is None:
                return f"No element found for selector: {selector}"
        else:
            root_el = page

        headings = await root_el.query_selector_all("h1, h2, h3, h4, h5, h6")
        lines: list[str] = []
        for h in headings:
            tag = await h.evaluate("el => el.tagName.toLowerCase()")
            level = int(tag[1]) if tag[1].isdigit() else 0
            text = (await h.inner_text()).strip()
            indent = "  " * (level - 1)
            lines.append(f"{indent}{'#' * level} {text}")

        result = "\n".join(lines)
        return truncate(result)

    # --- main mode: hide boilerplate, extract main content ---
    if mode == "main":
        await _hide_boilerplate(page)
        try:
            if selector:
                el = await page.query_selector(selector)
                if el is None:
                    return f"No element found for selector: {selector}"
                content = await el.inner_text()
            else:
                target, used_sel = await _extract_main_content(page)
                if target:
                    content = await target.inner_text()
                else:
                    content = await page.inner_text()
            return truncate(content.strip())
        finally:
            await _restore_boilerplate(page)

    # --- text mode (default, legacy behavior) ---
    if selector:
        el = await page.query_selector(selector)
        if el is None:
            return f"No element found for selector: {selector}"
        content = await el.inner_text()
    else:
        content = await page.inner_text()

    return truncate(content)


def register_scraping_tools(mcp: object) -> None:
    """Register scraping tools with the FastMCP server."""
    mcp.add_tool(browser_scrape)
