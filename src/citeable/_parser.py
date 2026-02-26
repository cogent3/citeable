"""BibTeX string parser — single-record ``from_bibtex_string``."""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

from citeable._entries import (
    Article,
    Book,
    CitationBase,
    InProceedings,
    Misc,
    Software,
    TechReport,
    Thesis,
)

_ENTRY_START_RE = re.compile(r"@(\w+)\s*\{")

_TYPE_MAP: dict[str, type[CitationBase]] = {
    "article": Article,
    "book": Book,
    "inproceedings": InProceedings,
    "techreport": TechReport,
    "phdthesis": Thesis,
    "mastersthesis": Thesis,
    "software": Software,
    "misc": Misc,
}


def _extract_entries(bibtex: str) -> list[tuple[str, str, str]]:
    """Return list of ``(entry_type, cite_key, body)`` tuples."""
    results: list[tuple[str, str, str]] = []
    for m in _ENTRY_START_RE.finditer(bibtex):
        entry_type = m.group(1)
        start = m.end()
        depth = 1
        pos = start
        while pos < len(bibtex) and depth > 0:
            if bibtex[pos] == "{":
                depth += 1
            elif bibtex[pos] == "}":
                depth -= 1
            pos += 1
        body = bibtex[start : pos - 1]
        comma_idx = body.find(",")
        if comma_idx == -1:
            cite_key = body.strip()
            fields_body = ""
        else:
            cite_key = body[:comma_idx].strip()
            fields_body = body[comma_idx + 1 :]
        results.append((entry_type, cite_key, fields_body))
    return results


def _normalise_author(name: str) -> str:
    """Normalise an author name to ``"Last, First"`` format."""
    name = name.strip()
    if "," in name:
        return name
    parts = name.split()
    return name if len(parts) <= 1 else f"{parts[-1]}, {' '.join(parts[:-1])}"


def _parse_authors(raw: str) -> list[str]:
    return [_normalise_author(a) for a in raw.split(" and ")]


_FIELD_START_RE = re.compile(r"^\s*(\w+)\s*=\s*", re.MULTILINE)


def _extract_value(raw: str) -> str:
    """Extract a field value from the text after ``=``.

    Handles brace-delimited (with nesting), quoted, and bare values.
    """
    raw = raw.strip()
    if raw.startswith("{"):
        depth = 0
        for i, ch in enumerate(raw):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return raw[1:i]
    elif raw.startswith('"'):
        end = raw.index('"', 1)
        return raw[1:end]
    else:
        return raw.rstrip(",").strip()
    return raw


def _parse_fields(body: str) -> dict[str, str]:
    """Parse BibTeX fields supporting braced, quoted, and bare values."""
    matches = list(_FIELD_START_RE.finditer(body))
    fields: dict[str, str] = {}
    for i, m in enumerate(matches):
        name = m.group(1).lower()
        val_start = m.end()
        val_end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        fields[name] = _extract_value(body[val_start:val_end])
    return fields


def _common_kwargs(
    fields: dict[str, str],
    cite_key: str,
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {"key": cite_key}
    if "author" in fields:
        kwargs["author"] = _parse_authors(fields["author"])
    if "title" in fields:
        kwargs["title"] = fields["title"]
    if "year" in fields:
        kwargs["year"] = int(fields["year"])
    for name in ("doi", "url", "note"):
        if name in fields:
            kwargs[name] = fields[name]
    return kwargs


def _article_kwargs(fields: dict[str, str]) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    if "journal" in fields:
        kwargs["journal"] = fields["journal"]
    if "volume" in fields:
        kwargs["volume"] = int(fields["volume"])
    if "pages" in fields:
        kwargs["pages"] = fields["pages"]
    if "article_number" in fields:
        kwargs["article_number"] = fields["article_number"]
    if "number" in fields:
        kwargs["number"] = int(fields["number"])
    return kwargs


def _book_kwargs(fields: dict[str, str]) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    if "publisher" in fields:
        kwargs["publisher"] = fields["publisher"]
    if "edition" in fields:
        kwargs["edition"] = fields["edition"]
    if "editor" in fields:
        kwargs["editor"] = _parse_authors(fields["editor"])
    return kwargs


def _inproceedings_kwargs(fields: dict[str, str]) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    if "booktitle" in fields:
        kwargs["booktitle"] = fields["booktitle"]
    if "pages" in fields:
        kwargs["pages"] = fields["pages"]
    if "publisher" in fields:
        kwargs["publisher"] = fields["publisher"]
    if "editor" in fields:
        kwargs["editor"] = _parse_authors(fields["editor"])
    return kwargs


def _techreport_kwargs(fields: dict[str, str]) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    if "institution" in fields:
        kwargs["institution"] = fields["institution"]
    if "number" in fields:
        kwargs["number"] = fields["number"]
    return kwargs


def _thesis_kwargs(
    fields: dict[str, str],
    entry_type: str,
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    if "school" in fields:
        kwargs["school"] = fields["school"]
    kwargs["thesis_type"] = "phd" if entry_type == "phdthesis" else "masters"
    return kwargs


def _software_kwargs(fields: dict[str, str]) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        name: fields[name]
        for name in ("publisher", "version", "license")
        if name in fields
    }
    return kwargs


_KwargsFunc = Callable[[dict[str, str]], dict[str, Any]]

_TYPE_KWARGS: dict[type[CitationBase], _KwargsFunc] = {
    Article: _article_kwargs,
    Book: _book_kwargs,
    InProceedings: _inproceedings_kwargs,
    TechReport: _techreport_kwargs,
    Software: _software_kwargs,
}


def from_bibtex_string(bibtex: str) -> CitationBase:
    """Parse a single BibTeX record and return the corresponding object."""
    entries = _extract_entries(bibtex)
    if not entries:
        msg = "No BibTeX entry found in input string"
        raise ValueError(msg)
    if len(entries) > 1:
        msg = "Multiple BibTeX entries found; only single-record strings are supported"
        raise ValueError(msg)

    entry_type_raw, cite_key, body = entries[0]
    entry_type = entry_type_raw.lower()

    if entry_type not in _TYPE_MAP:
        msg = f"Unsupported BibTeX entry type: @{entry_type}"
        raise ValueError(msg)

    cls = _TYPE_MAP[entry_type]
    fields = _parse_fields(body)
    kwargs = _common_kwargs(fields, cite_key)

    if cls is Thesis:
        kwargs.update(_thesis_kwargs(fields, entry_type))
    elif cls in _TYPE_KWARGS:
        kwargs.update(_TYPE_KWARGS[cls](fields))

    return cls(**kwargs)
