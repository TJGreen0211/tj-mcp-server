import re
from urllib.parse import urlparse

from fastmcp import FastMCP
from playwright.async_api import async_playwright

mcp = FastMCP("playwright-search-persistent")
_browser = None


async def get_browser():
    global _browser
    if _browser is None:
        p = await async_playwright().start()
        _browser = await p.chromium.launch(headless=True)
    return _browser


@mcp.tool()
async def search_web(query: str, max_results: int = 5) -> list[dict]:
    browser = await get_browser()
    # ... same logic, but use `browser.new_context()` per call
    # Close context after each search, keep browser alive
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        viewport={"width": 1280, "height": 720}
    )
    page = await context.new_page()

    try:
        # Use /html/ endpoint for server-rendered results (more stable)
        url = f"https://duckduckgo.com/html/?q={query}"
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)

        # Wait for results container
        await page.wait_for_selector(".result", timeout=15000)

        results = []
        items = await page.query_selector_all(".result")

        for item in items[:max_results]:
            try:
                title_el = await item.query_selector(".result__title a")
                url_el = await item.query_selector(".result__url")
                snippet_el = await item.query_selector(".result__snippet")

                if title_el and url_el:
                    title = await title_el.text_content()
                    url = await url_el.text_content()
                    snippet = (await snippet_el.text_content()).strip() if snippet_el else ""

                    results.append({
                        "title": title.strip(),
                        "url": url.strip(),
                        "snippet": snippet
                    })
            except Exception:
                continue  # Skip malformed results

        return results

    except Exception as e:
        return [{"error": f"Search failed: {str(e)}"}]
    finally:
        await context.close()


# ──────────────────────────────────────────────────────────────
# TOOL 2: Direct URL Browsing
# ──────────────────────────────────────────────────────────────
@mcp.tool()
async def browse_url(
    url: str,
    extract_html: bool = False,
    max_chars: int = 8000
) -> dict:
    """Navigate to a direct URL and extract its content for LLM consumption.

    Args:
        url: Full URL to browse (must include http:// or https://)
        extract_html: If True, returns raw HTML. False returns cleaned text.
        max_chars: Maximum characters to return (prevents token overflow)
    """
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return {"url": url, "status": "error", "error": "Invalid URL. Must include http:// or https://"}

    browser = await get_browser()
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (compatible; MCPBot/1.0)",
        viewport={"width": 1280, "height": 800}
    )
    page = await context.new_page()

    try:
        # Wait for network idle (better for SPAs/modern sites)
        await page.goto(url, wait_until="networkidle", timeout=30000)
        title = await page.title()

        if extract_html:
            content = await page.content()
        else:
            # Clean extraction: remove scripts, styles, nav, footers
            content = await page.evaluate("""
                () => {
                    const clone = document.body.cloneNode(true);
                    clone.querySelectorAll(
                                            'script,style,noscript,iframe,nav,footer,header,.ad,.ads,.sidebar,.cookie-banner'
                                        ).forEach(el => el.remove());
                    return clone.innerText;
                }
            """)

        # Normalize whitespace & enforce limit
        content = re.sub(r'\s+', ' ', content).strip()
        if len(content) > max_chars:
            content = content[:max_chars] + "\n\n[Content truncated to prevent token overflow]"

        return {
            "url": url,
            "title": title,
            "status": "success",
            "content": content,
            "content_length": len(content)
        }
    except Exception as e:
        return {"url": url, "status": "error", "error": str(e)}
    finally:
        await context.close()
