from collections.abc import Callable, Iterator, Mapping
from typing import Any, Self

class Request:
    url: str

class Response:
    status_code: int
    headers: Mapping[str, str]
    content: bytes
    text: str
    url: str
    encoding: str | None

    def __init__(
        self,
        status_code: int,
        *,
        content: bytes | None = ...,
        headers: Mapping[str, str] | None = ...,
        json: Any | None = ...,
    ) -> None: ...
    def json(self) -> Any: ...
    def raise_for_status(self) -> None: ...
    def iter_bytes(self, *, chunk_size: int = ...) -> Iterator[bytes]: ...

class MockTransport:
    def __init__(self, handler: Callable[[Request], Response]) -> None: ...

class _StreamContextManager:
    def __enter__(self) -> Response: ...
    def __exit__(self, exc_type: object, exc: object, tb: object) -> None: ...

class Client:
    def __init__(
        self,
        *,
        follow_redirects: bool | None = ...,
        timeout: float | None = ...,
        transport: MockTransport | None = ...,
    ) -> None: ...
    def get(
        self,
        url: str,
        *,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
    ) -> Response: ...
    def stream(
        self,
        method: str,
        url: str,
        *,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
    ) -> _StreamContextManager: ...
    def close(self) -> None: ...
    @property
    def is_closed(self) -> bool: ...
    def __enter__(self) -> Self: ...
    def __exit__(self, exc_type: object, exc: object, tb: object) -> None: ...
