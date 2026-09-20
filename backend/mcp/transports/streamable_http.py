"""Streamable HTTP transport (MCP SDK streamablehttp_client)."""

from __future__ import annotations

import inspect
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, Optional, Tuple
from urllib.parse import urljoin

import httpx

from backend.mcp.sdk import import_mcp_sdk_submodule

_streamable_http_mod = import_mcp_sdk_submodule("mcp.client.streamable_http")
streamablehttp_client = getattr(
    _streamable_http_mod,
    "streamablehttp_client",
    getattr(_streamable_http_mod, "streamable_http_client", None),
)
if streamablehttp_client is None:
    raise ImportError(
        "MCP SDK: neither 'streamablehttp_client' nor 'streamable_http_client' "
        "found in mcp.client.streamable_http"
    )

from backend.mcp.client import create_httpx_client, create_insecure_httpx_client


@asynccontextmanager
async def open_streamable_http_client(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = None,
    sse_read_timeout: Optional[float] = None,
) -> AsyncIterator[Tuple[Any, Any, Any]]:
    """
    Обёртка над streamablehttp_client для обратной совместимости MCP SDK.

    Старая SDK (<=1.8): streamablehttp_client(url, headers=None, timeout=..., sse_read_timeout=...)
    Новая SDK (>=1.9): streamable_http_client(url, http_client=None, terminate_on_close=True)
    """
    sig = inspect.signature(streamablehttp_client)
    has_headers = "headers" in sig.parameters

    if has_headers:
        # Старая SDK: передаём headers/timeout/sse_read_timeout напрямую
        kwargs = {}
        if headers is not None:
            kwargs["headers"] = headers
        if timeout is not None:
            kwargs["timeout"] = timeout
        if sse_read_timeout is not None:
            kwargs["sse_read_timeout"] = sse_read_timeout
        async with streamablehttp_client(url, **kwargs) as streams:
            yield streams
    else:
        # Новая SDK: создаём httpx.AsyncClient и передаём через http_client
        httpx_timeout = httpx.Timeout(
            timeout or 30.0,
            read=sse_read_timeout or 300.0
        )
        client_kwargs = {
            "headers": headers or {},
            "follow_redirects": True,
            "timeout": httpx_timeout,
        }
        httpx_client = httpx.AsyncClient(**client_kwargs)
        try:
            async with streamablehttp_client(url, http_client=httpx_client) as streams:
                yield streams
        finally:
            await httpx_client.aclose()


def build_mcp_http_url(base_url: str, base_path: str) -> str:
    root = str(base_url or "").strip().rstrip("/")
    path = str(base_path or "/mcp").strip()
    if not path.startswith("/"):
        path = f"/{path}"
    return urljoin(f"{root}/", path.lstrip("/"))


async def connect_streamable_http(
    client,
    *,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 120.0,
    verify_ssl: bool = True,
) -> None:
    factory = create_httpx_client if verify_ssl else create_insecure_httpx_client
    streams_context = open_streamable_http_client(

        url,
        headers=headers,
        timeout=timeout,
        sse_read_timeout=None,        
    )
    await client.connect_streams(streams_context, init_timeout=min(timeout, 30.0))
