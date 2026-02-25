"""JSON serialisation helpers for citation collections."""

from __future__ import annotations

import json
import pathlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

from citeable._entries import CitationBase


def to_jsons(citations: Iterable[CitationBase]) -> str:
    """Return a JSON string from an iterable of citations."""
    return json.dumps([c.to_dict() for c in citations])


def from_jsons(data: str) -> list[CitationBase]:
    """Return a list of citations from a JSON string."""
    return [CitationBase.from_dict(d) for d in json.loads(data)]


def write_json(*, citations: Iterable[CitationBase], path: str | pathlib.Path) -> None:
    """Write citations to a JSON file at *path*."""
    pathlib.Path(path).write_text(to_jsons(citations))


def load_json(path: str | pathlib.Path) -> list[CitationBase]:
    """Read citations from a JSON file at *path*."""
    return from_jsons(pathlib.Path(path).read_text())
