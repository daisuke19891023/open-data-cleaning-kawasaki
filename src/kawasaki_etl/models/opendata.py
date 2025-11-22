from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True)
class OpenDataResource:
    """単一のオープンデータファイルに関するメタデータ."""

    title: str
    url: str
    file_format: str
    updated_at: str
    description: str | None = None

    @property
    def filename(self) -> str:
        """リソースURLから取得したファイル名."""
        parsed = urlparse(self.url)
        return Path(parsed.path).name


@dataclass(frozen=True)
class OpenDataPage:
    """オープンデータページ内のリンク群とメタデータ."""

    identifier: str
    page_url: str
    description: str
    resources: tuple[OpenDataResource, ...]

    @property
    def storage_dirname(self) -> str:
        """ページを保存する際のディレクトリ名."""
        return self.identifier
