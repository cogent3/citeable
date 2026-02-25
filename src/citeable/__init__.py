"""citeable — structured BibTeX citations for cogent3 plugins."""

from importlib import metadata as _metadata

from citeable._entries import (
    Article,
    Book,
    Citation,
    CitationBase,
    InProceedings,
    Misc,
    Software,
    TechReport,
    Thesis,
)
from citeable._json import from_jsons, load_json, to_jsons, write_json
from citeable._keys import assign_unique_keys, write_bibtex
from citeable._parser import from_bibtex_string

__version__ = _metadata.version("citeable")

__all__ = [
    "Article",
    "Book",
    "Citation",
    "CitationBase",
    "InProceedings",
    "Misc",
    "Software",
    "TechReport",
    "Thesis",
    "__version__",
    "assign_unique_keys",
    "from_bibtex_string",
    "from_jsons",
    "load_json",
    "to_jsons",
    "write_bibtex",
    "write_json",
]
