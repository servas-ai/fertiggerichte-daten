"""MCP tools (stdio) via the official `mcp` SDK: pip install mcp; python -m food_company.mcp_server"""
from mcp.server.fastmcp import FastMCP
from . import registries as r
m = FastMCP("food-company")
@m.tool()
def company_lookup(name: str, country: str = "") -> dict:
    """GLEIF legal entity + register id (FN) + parent group for a company name."""
    return r.company(name, country or None)
@m.tool()
def company_children(lei: str) -> list:
    """Direct subsidiaries (GLEIF level-2 relationships)."""
    return r.gleif_children(lei)
@m.tool()
def uid_check(vat: str) -> dict:
    """Validate an EU VAT/UID number via EU VIES."""
    return r.vies_check(vat)
@m.tool()
def northdata(name: str) -> dict:
    """North Data public page facts (or official API if NORTHDATA_API_KEY set)."""
    return r.northdata_page(name)
if __name__ == "__main__": m.run()
