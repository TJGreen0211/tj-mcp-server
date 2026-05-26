"""Holder for Playwright browser, context, and page. Injected into tools via lifespan context."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.async_api import Browser, BrowserContext, Page, Playwright


class BrowserState:
    """Shared browser state created at startup and closed at shutdown."""

    def __init__(self) -> None:
        self._playwright: "Playwright | None" = None
        self._browser: "Browser | None" = None
        self._context: "BrowserContext | None" = None
        self._page: "Page | None" = None

    @property
    def playwright(self) -> "Playwright":
        """Playwright instance. Raises if not initialized."""
        if self._playwright is None:
            raise RuntimeError("Browser not started; lifespan may not have run.")
        return self._playwright

    @property
    def browser(self) -> "Browser":
        """Browser instance. Raises if not initialized."""
        if self._browser is None:
            raise RuntimeError("Browser not started; lifespan may not have run.")
        return self._browser

    @property
    def context(self) -> "BrowserContext":
        """Browser context. Raises if not initialized."""
        if self._context is None:
            raise RuntimeError("Browser not started; lifespan may not have run.")
        return self._context

    @property
    def page(self) -> "Page":
        """Current page. Raises if not initialized."""
        if self._page is None:
            raise RuntimeError("No page; browser may not have been started.")
        return self._page

    def set_playwright(self, p: "Playwright") -> None:
        self._playwright = p

    def set_browser(self, b: "Browser") -> None:
        self._browser = b

    def set_context(self, c: "BrowserContext") -> None:
        self._context = c

    def set_page(self, p: "Page") -> None:
        self._page = p

    async def close(self) -> None:
        """Close page, context, browser, and Playwright in order."""
        if self._page:
            await self._page.close()
            self._page = None
        if self._context:
            await self._context.close()
            self._context = None
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None
