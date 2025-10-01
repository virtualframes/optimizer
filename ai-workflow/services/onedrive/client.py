import os
import msal
import aiohttp

TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
SCOPE = [os.getenv("GRAPH_SCOPE")]

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
GRAPH_API = "https://graph.microsoft.com/v1.0"

_app = msal.ConfidentialClientApplication(
    CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
)

async def get_access_token() -> str:
    """Acquire token from MSAL cache or refresh."""
    result = _app.acquire_token_silent(SCOPE, account=None)
    if not result:
        result = _app.acquire_token_for_client(scopes=SCOPE)
    return result["access_token"]

async def _make_graph_api_call(session: aiohttp.ClientSession, url: str, method: str = "GET", **kwargs):
    token = await get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    if "headers" in kwargs:
        headers.update(kwargs["headers"])

    async with session.request(method, url, headers=headers, **kwargs) as resp:
        resp.raise_for_status()
        if resp.content_type == 'application/json':
            return await resp.json()
        return await resp.text()

async def list_notebooks(session: aiohttp.ClientSession) -> list[dict]:
    """List all OneNote notebooks."""
    url = f"{GRAPH_API}/me/onenote/notebooks"
    response = await _make_graph_api_call(session, url)
    return response.get("value", [])

async def list_sections(session: aiohttp.ClientSession, notebook_id: str) -> list[dict]:
    """List all sections in a given notebook."""
    url = f"{GRAPH_API}/me/onenote/notebooks/{notebook_id}/sections"
    response = await _make_graph_api_call(session, url)
    return response.get("value", [])

async def list_pages(session: aiohttp.ClientSession, section_id: str) -> list[dict]:
    """List all pages in a given section."""
    url = f"{GRAPH_API}/me/onenote/sections/{section_id}/pages"
    response = await _make_graph_api_call(session, url)
    return response.get("value", [])

async def get_page_content(session: aiohttp.ClientSession, page_id: str) -> str:
    """Get the HTML content of a given page."""
    url = f"{GRAPH_API}/me/onenote/pages/{page_id}/content"
    return await _make_graph_api_call(session, url, headers={"Accept": "text/html"})