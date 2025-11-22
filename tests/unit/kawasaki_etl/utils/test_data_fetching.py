# ruff: noqa:D103

from __future__ import annotations

from typing import TYPE_CHECKING

from httpx import Client, MockTransport, Request, Response

from kawasaki_etl.utils import WebDataFetcher

if TYPE_CHECKING:
    from pathlib import Path


def test_fetch_bytes_uses_client() -> None:
    payload = b"hello"

    def handler(request: Request) -> Response:  # noqa: ARG001
        return Response(200, content=payload)

    client = Client(transport=MockTransport(handler))
    fetcher = WebDataFetcher(client)

    assert fetcher.fetch_bytes("https://example.test/data") == payload


def test_fetch_text_respects_encoding() -> None:
    text_value = "こんにちは"

    def handler(request: Request) -> Response:  # noqa: ARG001
        return Response(
            200,
            content=text_value.encode("shift_jis"),
            headers={"content-type": "text/plain; charset=shift_jis"},
        )

    client = Client(transport=MockTransport(handler))
    fetcher = WebDataFetcher(client)

    assert (
        fetcher.fetch_text(
            "https://example.test/text",
            encoding="shift_jis",
        )
        == text_value
    )


def test_stream_to_file_writes_contents(tmp_path: Path) -> None:
    content = b"abc123"

    def handler(request: Request) -> Response:  # noqa: ARG001
        return Response(200, content=content)

    client = Client(transport=MockTransport(handler))
    fetcher = WebDataFetcher(client)

    destination = tmp_path / "download.bin"
    result_path = fetcher.stream_to_file("https://example.test/bin", destination)

    assert result_path == destination
    assert destination.read_bytes() == content


def test_fetch_json_parses_payload() -> None:
    def handler(request: Request) -> Response:  # noqa: ARG001
        return Response(200, json={"ok": True, "count": 2})

    client = Client(transport=MockTransport(handler))
    fetcher = WebDataFetcher(client)

    assert fetcher.fetch_json("https://example.test/data.json") == {
        "ok": True,
        "count": 2,
    }


def test_context_manager_closes_owned_client() -> None:
    def handler(request: Request) -> Response:  # noqa: ARG001
        return Response(200, json={"ok": True})

    client = Client(transport=MockTransport(handler))

    with WebDataFetcher(client) as fetcher:
        assert fetcher.fetch_json("https://example.test/ctx") == {"ok": True}

    assert fetcher.is_closed


def test_close_does_not_shutdown_external_client() -> None:
    def handler(request: Request) -> Response:  # noqa: ARG001
        return Response(200, content=b"done")

    client = Client(transport=MockTransport(handler))
    fetcher = WebDataFetcher(client)

    fetcher.close()

    assert not client.is_closed
    client.close()
