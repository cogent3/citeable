"""Citation entry type classes for all supported BibTeX types."""

from __future__ import annotations

from abc import ABC, abstractmethod

from citeable._keys import generate_key
from citeable._validate import extract_surname, require_field, require_non_empty_authors


def _format_bibtex_field(name: str, value: str) -> str:
    return f"  {name:<10}= {{{value}}},"


def _author_str(authors: list[str]) -> str:
    return " and ".join(authors)


def _author_summary(authors: list[str]) -> str:
    surname = extract_surname(authors[0])
    return f"{surname} et al." if len(authors) > 1 else surname


def _title_excerpt(title: str, max_len: int = 50) -> str:
    return title if len(title) <= max_len else title[:max_len] + "\u2026"


def _content_fields(obj: object, exclude: set[str]) -> tuple[object, ...]:
    """Return a tuple of content field values for equality/hashing.

    Lists are converted to tuples so the result is hashable.
    """
    vals: list[object] = []
    vals.extend(
        tuple(v) if isinstance(v, list) else v
        for k, v in sorted(vars(obj).items())
        if k not in exclude
    )
    return tuple(vals)


_EXCLUDED: set[str] = {"key", "app"}


class CitationBase(ABC):
    """Abstract base class for all citation entry types."""

    author: list[str]
    title: str
    year: int
    doi: str | None
    url: str | None
    note: str | None
    key: str
    app: str | None

    def _init_base(
        self,
        author: list[str],
        title: str,
        year: int,
        *,
        doi: str | None = None,
        url: str | None = None,
        note: str | None = None,
        key: str | None = None,
        app: str | None = None,
    ) -> None:
        """Set common fields shared by all citation types."""
        require_non_empty_authors(author, type(self).__name__)
        self.author = author
        self.title = title
        self.year = year
        self.doi = doi
        self.url = url
        self.note = note
        self.key = key if key is not None else generate_key(author, year)
        self.app = app

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if type(self) is not type(other):
            return NotImplemented
        return _content_fields(self, _EXCLUDED) == _content_fields(other, _EXCLUDED)

    def __hash__(self) -> int:
        return hash((type(self).__name__, _content_fields(self, _EXCLUDED)))

    def summary(self) -> tuple[str, str]:
        """Return ``(app_name, citation_string)``."""
        app_name = self.app if self.app is not None else ""
        auth = _author_summary(self.author)
        excerpt = _title_excerpt(self.title)
        return (app_name, f"{auth} {self.year} {excerpt}")

    def __repr__(self) -> str:
        fields = self._repr_fields()
        auto_key = generate_key(self.author, self.year)
        if self.key != auto_key:
            fields.insert(0, ("key", self.key))
        parts = [f"    {name}={value!r}," for name, value in fields]
        body = "\n".join(parts)
        return f"{type(self).__name__}(\n{body}\n)"

    def _append_common_bibtex(self, lines: list[str]) -> None:
        """Append doi/url/note BibTeX fields if set."""
        if self.doi is not None:
            lines.append(_format_bibtex_field("doi", self.doi))
        if self.url is not None:
            lines.append(_format_bibtex_field("url", self.url))
        if self.note is not None:
            lines.append(_format_bibtex_field("note", self.note))

    def _append_common_optional_repr(self, fields: list[tuple[str, object]]) -> None:
        """Append doi/url/note to repr field list if set."""
        if self.doi is not None:
            fields.append(("doi", self.doi))
        if self.url is not None:
            fields.append(("url", self.url))
        if self.note is not None:
            fields.append(("note", self.note))

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serialisable dict including a ``"type"`` discriminator."""
        return {"type": type(self).__name__, **vars(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> CitationBase:
        """Reconstruct a citation from a dict produced by :meth:`to_dict`.

        Raises ``ValueError`` if the ``"type"`` key is missing or unknown.
        """
        data = dict(data)  # shallow copy so we don't mutate the caller's dict
        type_name = data.pop("type", None)
        if type_name is None:
            msg = "dict is missing required 'type' key"
            raise ValueError(msg)
        entry_cls = _ENTRY_TYPES.get(str(type_name))
        if entry_cls is None:
            msg = f"unknown citation type {type_name!r}"
            raise ValueError(msg)
        return entry_cls(**data)

    @abstractmethod
    def _repr_fields(self) -> list[tuple[str, object]]:
        """Return the list of ``(name, value)`` pairs for ``__repr__``."""


# Keep Citation as a public alias for the base class.
Citation = CitationBase


class Article(CitationBase):
    """An ``@article`` BibTeX entry."""

    journal: str
    volume: int
    pages: str | None
    article_number: str | None
    number: int | None

    def __init__(
        self,
        author: list[str],
        title: str,
        year: int,
        journal: str,
        volume: int,
        *,
        pages: str | None = None,
        article_number: str | None = None,
        number: int | None = None,
        doi: str | None = None,
        url: str | None = None,
        note: str | None = None,
        key: str | None = None,
        app: str | None = None,
    ) -> None:
        require_field(journal, "journal", "Article")
        require_field(volume, "volume", "Article")
        if pages is None and article_number is None:
            msg = "Article requires 'pages' or 'article_number'; both are None"
            raise ValueError(msg)

        self._init_base(
            author, title, year, doi=doi, url=url, note=note, key=key, app=app
        )
        self.journal = journal
        self.volume = volume
        self.pages = pages
        self.article_number = article_number
        self.number = number

    def __str__(self) -> str:
        lines = [
            f"@article{{{self.key},",
            _format_bibtex_field("author", _author_str(self.author)),
            _format_bibtex_field("title", self.title),
            _format_bibtex_field("journal", self.journal),
            _format_bibtex_field("year", str(self.year)),
            _format_bibtex_field("volume", str(self.volume)),
        ]
        if self.number is not None:
            lines.append(_format_bibtex_field("number", str(self.number)))
        if self.pages is not None:
            lines.append(_format_bibtex_field("pages", self.pages))
        if self.article_number is not None:
            lines.append(_format_bibtex_field("article_number", self.article_number))
        self._append_common_bibtex(lines)
        lines.append("}")
        return "\n".join(lines)

    def _repr_fields(self) -> list[tuple[str, object]]:
        fields: list[tuple[str, object]] = [
            ("author", self.author),
            ("title", self.title),
            ("year", self.year),
            ("journal", self.journal),
            ("volume", self.volume),
        ]
        if self.pages is not None:
            fields.append(("pages", self.pages))
        if self.article_number is not None:
            fields.append(("article_number", self.article_number))
        if self.number is not None:
            fields.append(("number", self.number))
        self._append_common_optional_repr(fields)
        return fields


class Book(CitationBase):
    """A ``@book`` BibTeX entry."""

    publisher: str
    edition: str | None
    editor: list[str] | None

    def __init__(
        self,
        author: list[str],
        title: str,
        year: int,
        publisher: str,
        *,
        edition: str | None = None,
        editor: list[str] | None = None,
        doi: str | None = None,
        url: str | None = None,
        note: str | None = None,
        key: str | None = None,
        app: str | None = None,
    ) -> None:
        require_field(publisher, "publisher", "Book")

        self._init_base(
            author, title, year, doi=doi, url=url, note=note, key=key, app=app
        )
        self.publisher = publisher
        self.edition = edition
        self.editor = editor

    def __str__(self) -> str:
        lines = [
            f"@book{{{self.key},",
            _format_bibtex_field("author", _author_str(self.author)),
            _format_bibtex_field("title", self.title),
            _format_bibtex_field("publisher", self.publisher),
            _format_bibtex_field("year", str(self.year)),
        ]
        if self.edition is not None:
            lines.append(_format_bibtex_field("edition", self.edition))
        if self.editor is not None:
            lines.append(_format_bibtex_field("editor", _author_str(self.editor)))
        self._append_common_bibtex(lines)
        lines.append("}")
        return "\n".join(lines)

    def _repr_fields(self) -> list[tuple[str, object]]:
        fields: list[tuple[str, object]] = [
            ("author", self.author),
            ("title", self.title),
            ("year", self.year),
            ("publisher", self.publisher),
        ]
        if self.edition is not None:
            fields.append(("edition", self.edition))
        if self.editor is not None:
            fields.append(("editor", self.editor))
        self._append_common_optional_repr(fields)
        return fields


class InProceedings(CitationBase):
    """An ``@inproceedings`` BibTeX entry."""

    booktitle: str
    pages: str | None
    publisher: str | None
    editor: list[str] | None

    def __init__(
        self,
        author: list[str],
        title: str,
        year: int,
        booktitle: str,
        *,
        pages: str | None = None,
        publisher: str | None = None,
        editor: list[str] | None = None,
        doi: str | None = None,
        url: str | None = None,
        note: str | None = None,
        key: str | None = None,
        app: str | None = None,
    ) -> None:
        require_field(booktitle, "booktitle", "InProceedings")

        self._init_base(
            author, title, year, doi=doi, url=url, note=note, key=key, app=app
        )
        self.booktitle = booktitle
        self.pages = pages
        self.publisher = publisher
        self.editor = editor

    def __str__(self) -> str:
        lines = [
            f"@inproceedings{{{self.key},",
            _format_bibtex_field("author", _author_str(self.author)),
            _format_bibtex_field("title", self.title),
            _format_bibtex_field("booktitle", self.booktitle),
            _format_bibtex_field("year", str(self.year)),
        ]
        if self.pages is not None:
            lines.append(_format_bibtex_field("pages", self.pages))
        if self.publisher is not None:
            lines.append(_format_bibtex_field("publisher", self.publisher))
        if self.editor is not None:
            lines.append(_format_bibtex_field("editor", _author_str(self.editor)))
        self._append_common_bibtex(lines)
        lines.append("}")
        return "\n".join(lines)

    def _repr_fields(self) -> list[tuple[str, object]]:
        fields: list[tuple[str, object]] = [
            ("author", self.author),
            ("title", self.title),
            ("year", self.year),
            ("booktitle", self.booktitle),
        ]
        if self.pages is not None:
            fields.append(("pages", self.pages))
        if self.publisher is not None:
            fields.append(("publisher", self.publisher))
        if self.editor is not None:
            fields.append(("editor", self.editor))
        self._append_common_optional_repr(fields)
        return fields


class TechReport(CitationBase):
    """A ``@techreport`` BibTeX entry."""

    institution: str
    number: str | None

    def __init__(
        self,
        author: list[str],
        title: str,
        year: int,
        institution: str,
        *,
        number: str | None = None,
        doi: str | None = None,
        url: str | None = None,
        note: str | None = None,
        key: str | None = None,
        app: str | None = None,
    ) -> None:
        require_field(institution, "institution", "TechReport")

        self._init_base(
            author, title, year, doi=doi, url=url, note=note, key=key, app=app
        )
        self.institution = institution
        self.number = number

    def __str__(self) -> str:
        lines = [
            f"@techreport{{{self.key},",
            _format_bibtex_field("author", _author_str(self.author)),
            _format_bibtex_field("title", self.title),
            _format_bibtex_field("institution", self.institution),
            _format_bibtex_field("year", str(self.year)),
        ]
        if self.number is not None:
            lines.append(_format_bibtex_field("number", self.number))
        self._append_common_bibtex(lines)
        lines.append("}")
        return "\n".join(lines)

    def _repr_fields(self) -> list[tuple[str, object]]:
        fields: list[tuple[str, object]] = [
            ("author", self.author),
            ("title", self.title),
            ("year", self.year),
            ("institution", self.institution),
        ]
        if self.number is not None:
            fields.append(("number", self.number))
        self._append_common_optional_repr(fields)
        return fields


class Thesis(CitationBase):
    """A ``@phdthesis`` or ``@mastersthesis`` BibTeX entry."""

    school: str
    thesis_type: str

    def __init__(
        self,
        author: list[str],
        title: str,
        year: int,
        school: str,
        thesis_type: str,
        *,
        doi: str | None = None,
        url: str | None = None,
        note: str | None = None,
        key: str | None = None,
        app: str | None = None,
    ) -> None:
        require_field(school, "school", "Thesis")
        require_field(thesis_type, "thesis_type", "Thesis")
        if thesis_type not in ("phd", "masters"):
            msg = f"Thesis thesis_type must be 'phd' or 'masters'; got {thesis_type!r}"
            raise ValueError(msg)

        self._init_base(
            author, title, year, doi=doi, url=url, note=note, key=key, app=app
        )
        self.school = school
        self.thesis_type = thesis_type

    def __str__(self) -> str:
        bib_type = "phdthesis" if self.thesis_type == "phd" else "mastersthesis"
        lines = [
            f"@{bib_type}{{{self.key},",
            _format_bibtex_field("author", _author_str(self.author)),
            _format_bibtex_field("title", self.title),
            _format_bibtex_field("school", self.school),
            _format_bibtex_field("year", str(self.year)),
        ]
        self._append_common_bibtex(lines)
        lines.append("}")
        return "\n".join(lines)

    def _repr_fields(self) -> list[tuple[str, object]]:
        fields: list[tuple[str, object]] = [
            ("author", self.author),
            ("title", self.title),
            ("year", self.year),
            ("school", self.school),
            ("thesis_type", self.thesis_type),
        ]
        self._append_common_optional_repr(fields)
        return fields


class Software(CitationBase):
    """A ``@software`` BibTeX entry."""

    publisher: str | None
    version: str | None
    license: str | None

    def __init__(
        self,
        author: list[str],
        title: str,
        year: int,
        *,
        publisher: str | None = None,
        version: str | None = None,
        license: str | None = None,
        doi: str | None = None,
        url: str | None = None,
        note: str | None = None,
        key: str | None = None,
        app: str | None = None,
    ) -> None:
        self._init_base(
            author, title, year, doi=doi, url=url, note=note, key=key, app=app
        )
        self.publisher = publisher
        self.version = version
        self.license = license

    def __str__(self) -> str:
        lines = [
            f"@software{{{self.key},",
            _format_bibtex_field("author", _author_str(self.author)),
            _format_bibtex_field("title", self.title),
            _format_bibtex_field("year", str(self.year)),
        ]
        if self.publisher is not None:
            lines.append(_format_bibtex_field("publisher", self.publisher))
        if self.version is not None:
            lines.append(_format_bibtex_field("version", self.version))
        if self.license is not None:
            lines.append(_format_bibtex_field("license", self.license))
        self._append_common_bibtex(lines)
        lines.append("}")
        return "\n".join(lines)

    def _repr_fields(self) -> list[tuple[str, object]]:
        fields: list[tuple[str, object]] = [
            ("author", self.author),
            ("title", self.title),
            ("year", self.year),
        ]
        if self.publisher is not None:
            fields.append(("publisher", self.publisher))
        if self.version is not None:
            fields.append(("version", self.version))
        if self.license is not None:
            fields.append(("license", self.license))
        self._append_common_optional_repr(fields)
        return fields


class Misc(CitationBase):
    """A ``@misc`` BibTeX entry."""

    def __init__(
        self,
        author: list[str],
        title: str,
        year: int,
        *,
        doi: str | None = None,
        url: str | None = None,
        note: str | None = None,
        key: str | None = None,
        app: str | None = None,
    ) -> None:
        self._init_base(
            author, title, year, doi=doi, url=url, note=note, key=key, app=app
        )

    def __str__(self) -> str:
        lines = [
            f"@misc{{{self.key},",
            _format_bibtex_field("author", _author_str(self.author)),
            _format_bibtex_field("title", self.title),
            _format_bibtex_field("year", str(self.year)),
        ]
        self._append_common_bibtex(lines)
        lines.append("}")
        return "\n".join(lines)

    def _repr_fields(self) -> list[tuple[str, object]]:
        fields: list[tuple[str, object]] = [
            ("author", self.author),
            ("title", self.title),
            ("year", self.year),
        ]
        self._append_common_optional_repr(fields)
        return fields


_ENTRY_TYPES: dict[str, type[CitationBase]] = {
    "Article": Article,
    "Book": Book,
    "InProceedings": InProceedings,
    "TechReport": TechReport,
    "Thesis": Thesis,
    "Software": Software,
    "Misc": Misc,
}
