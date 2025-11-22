"""Utilities for retrieving web-hosted open data resources."""

from __future__ import annotations

# pyright: reportUnknownMemberType=false, reportAttributeAccessIssue=false

from pathlib import Path
from typing import TYPE_CHECKING, Any, Self, cast

import httpx
from kawasaki_etl.base import BaseComponent

if TYPE_CHECKING:
    from collections.abc import Mapping

HTTPClient = Any
httpx = cast("Any", httpx)

TimeoutType = float | None


class WebDataFetcher(BaseComponent):
    """Fetch remote resources over HTTP(S)."""

    def __init__(
        self,
        client: HTTPClient | None = None,
        *,
        default_timeout: TimeoutType = 10.0,
    ) -> None:
        """Initialize the fetcher.

        Args:
            client: Optional pre-configured ``httpx.Client`` to reuse.
            default_timeout: Default timeout applied when a per-call override is not
                provided.

        """
        super().__init__()
        self._client: HTTPClient = client or httpx.Client(
            follow_redirects=True,
            timeout=default_timeout,
        )  # type: ignore[reportAttributeAccessIssue]
        self._owns_client = client is None
        self._default_timeout: TimeoutType = default_timeout

    def _resolve_timeout(
        self,
        timeout: TimeoutType,
    ) -> TimeoutType:
        return self._default_timeout if timeout is None else timeout

    def fetch_bytes(
        self,
        url: str,
        *,
        timeout: TimeoutType = None,
        headers: Mapping[str, str] | None = None,
    ) -> bytes:
        """Return the raw bytes from a URL."""
        resolved_timeout = self._resolve_timeout(timeout)
        self.logger.debug("Fetching bytes", url=url, timeout=resolved_timeout)
        response = self._client.get(url, timeout=resolved_timeout, headers=headers)
        response.raise_for_status()
        self.logger.info(
            "Fetched bytes",
            url=url,
            status_code=response.status_code,
            size=len(response.content),
        )
        return response.content

    def fetch_text(
        self,
        url: str,
        *,
        timeout: TimeoutType = None,
        encoding: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> str:
        """Return text content from a URL."""
        resolved_timeout = self._resolve_timeout(timeout)
        self.logger.debug(
            "Fetching text",
            url=url,
            timeout=resolved_timeout,
            encoding=encoding,
        )
        response = self._client.get(url, timeout=resolved_timeout, headers=headers)
        response.raise_for_status()
        if encoding:
            response.encoding = encoding
        text = response.text
        self.logger.info(
            "Fetched text",
            url=url,
            status_code=response.status_code,
            length=len(text),
        )
        return text

    def fetch_json(
        self,
        url: str,
        *,
        timeout: TimeoutType = None,
        headers: Mapping[str, str] | None = None,
    ) -> Any:
        """Return parsed JSON content from a URL."""
        resolved_timeout = self._resolve_timeout(timeout)
        self.logger.debug("Fetching JSON", url=url, timeout=resolved_timeout)
        response = self._client.get(url, timeout=resolved_timeout, headers=headers)
        response.raise_for_status()
        payload = response.json()
        self.logger.info(
            "Fetched JSON",
            url=url,
            status_code=response.status_code,
            payload_type=type(payload).__name__,
        )
        return payload

    def stream_to_file(
        self,
        url: str,
        destination: str | Path,
        *,
        chunk_size: int = 8192,
        timeout: TimeoutType = None,
        headers: Mapping[str, str] | None = None,
    ) -> Path:
        """Stream a remote file directly to disk."""
        target_path = Path(destination)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_timeout = self._resolve_timeout(timeout)
        self.logger.debug(
            "Streaming to file",
            url=url,
            destination=str(target_path),
            chunk_size=chunk_size,
            timeout=resolved_timeout,
        )

        with self._client.stream(
            "GET",
            url,
            timeout=resolved_timeout,
            headers=headers,
        ) as response:
            response.raise_for_status()
            with target_path.open("wb") as fp:
                for chunk in response.iter_bytes(chunk_size=chunk_size):
                    fp.write(chunk)

        self.logger.info(
            "Streamed file",
            url=url,
            destination=str(target_path),
            status_code=response.status_code,
            size=target_path.stat().st_size,
        )
        return target_path

    def close(self, *, force: bool = False) -> None:
        """Close the internal HTTP client.

        Args:
            force: When ``True``, close the client even if it was provided by the
                caller.

        """
        if (self._owns_client or force) and not self._client.is_closed:
            self._client.close()

    @property
    def is_closed(self) -> bool:
        """Return whether the underlying HTTP client has been closed."""
        return self._client.is_closed

    def __enter__(self) -> Self:
        """Enter the context manager and return ``self``."""
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        """Ensure the underlying client is closed on exit."""
        self.close(force=True)


def fetch_json(
    url: str,
    *,
    timeout: TimeoutType = 10.0,
    headers: Mapping[str, str] | None = None,
) -> Any:
    """Fetch JSON content with a short-lived client."""
    with WebDataFetcher(default_timeout=timeout) as fetcher:
        return fetcher.fetch_json(url, headers=headers)


__all__ = ["WebDataFetcher", "fetch_json"]
