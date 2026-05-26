"""Development entrypoint: run from project root without installing the package."""

import sys
from pathlib import Path

# Prepend src so "playwright_mcp" resolves
root = Path(__file__).resolve().parent
src = root / "src"
if str(src) not in sys.path:
    sys.path.insert(0, str(src))

from playwright_mcp.main import main

if __name__ == "__main__":
    main()
