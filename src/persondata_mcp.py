"""Start MCP-serveren for syntetiske kundedata: py -3.13 src/persondata_mcp.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.kunstpixel.persondata.mcp_server import mcp  # noqa: E402

if __name__ == "__main__":
    mcp.run()
