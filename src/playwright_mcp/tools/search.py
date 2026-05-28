"""Web search tool: query DuckDuckGo and return results."""

import asyncio
import re

from fastmcp import Context

from playwright_mcp.browser.state import BrowserState


async def web_search(ctx: Context, query: str, max_results: int = 10) -> list[dict]:
    """Search the web using DuckDuckGo. Returns a list of results with title, url, and snippet."""
    state: BrowserState = ctx.lifespan_context["browser_state"]
    logger = ctx.lifespan_context["logger"]
    logger.info("web_search", query=query, max_results=max_results)
    page = state.page

    search_url = f"https://duckduckgo.com/?q={query}&ia=web"
    await page.goto(search_url, wait_until="domcontentloaded")
    await asyncio.sleep(1.5)

    results = []

    result_elements = await page.query_selector_all('article[data-result-size]')
    if not result_elements:
        result_elements = await page.query_selector_all("article")

    for el in result_elements[:max_results]:
        try:
            url = await el.get_attribute("data-result-url") or ""
            if not url:
                link_el = await el.query_selector("a[href]")
                if link_el:
                    url = await link_el.get_attribute("href") or ""

            title_el = await el.query_selector("[data-result-title]")
            title = (await title_el.inner_text()).strip() if title_el else ""

            snippet_el = await el.query_selector("[data-result-snippet]")
            snippet = (await snippet_el.inner_text()).strip() if snippet_el else ""

            if title or url:
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                })
        except Exception:
            continue

    if not results:
        content = await page.inner_text()
        links = re.findall(r'https?://\S+', content)
        for link in links[:max_results]:
            if "duckduckgo.com" not in link:
                results.append({
                    "title": "",
                    "url": link,
                    "snippet": "",
                })

    if not results:
        return [{"title": "No results found", "url": "", "snippet": f"No results for query: {query}"}]

    return results


def register_search_tools(mcp: object) -> None:
    """Register search tools with the FastMCP server."""
    mcp.add_tool(web_search)
