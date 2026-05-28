"""Start and stop Playwright browser (Option A: single long-lived instance)."""

from fastmcp.server.lifespan import lifespan

from playwright_mcp.browser.state import BrowserState
from playwright_mcp.config import get_settings
from playwright_mcp.logging_ import get_logger
from playwright_mcp.memory.store import KnowledgeGraphManager

logger = get_logger(__name__)


@lifespan
async def create_browser_lifespan(server: object) -> dict:
    """Start Playwright and one browser/context/page; yield state for tools. Teardown on exit."""
    settings = get_settings()
    state = BrowserState()
    memory = KnowledgeGraphManager()
    try:
        from playwright.async_api import async_playwright

        logger.info("Starting browser", headless=settings.headless)
        pw = await async_playwright().start()
        state.set_playwright(pw)
        browser = await pw.chromium.launch(headless=settings.headless)
        state.set_browser(browser)
        context = await browser.new_context()
        state.set_context(context)
        page = await context.new_page()
        state.set_page(page)
        logger.info("Browser ready")
        yield {"browser_state": state, "logger": logger, "memory": memory}
    finally:
        logger.info("Closing browser")
        await state.close()
        logger.info("Browser closed")
