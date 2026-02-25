"""Tests for __str__, __repr__, summary(), and JSON serialisation."""

import pathlib

import pytest

from citeable import (
    Article,
    Book,
    CitationBase,
    InProceedings,
    Misc,
    Software,
    TechReport,
    Thesis,
    from_jsons,
    load_json,
    to_jsons,
    write_json,
)

# ── __str__ (BibTeX output) ─────────────────────────────────────────────


def test_article_str():
    a = Article(
        author=["Huttley, Gavin", "Caley, Katherine", "McArthur, Robert"],
        title="diverse-seq",
        journal="Journal of Open Source Software",
        year=2025,
        volume=10,
        number=110,
        pages="7765",
        doi="10.21105/joss.07765",
        url="https://doi.org/10.21105/joss.07765",
    )
    result = str(a)
    assert result.startswith("@article{Huttley.2025,")
    assert "author" in result
    assert "Huttley, Gavin and Caley, Katherine and McArthur, Robert" in result
    assert "journal" in result
    assert "volume" in result
    assert "number" in result
    assert "pages" in result
    assert "doi" in result
    assert "url" in result
    assert result.endswith("}")


def test_thesis_str_phd():
    t = Thesis(
        author=["Student, Alice"],
        title="My Thesis",
        year=2022,
        school="MIT",
        thesis_type="phd",
    )
    result = str(t)
    assert result.startswith("@phdthesis{")


def test_thesis_str_masters():
    t = Thesis(
        author=["Student, Bob"],
        title="My Thesis",
        year=2021,
        school="Oxford",
        thesis_type="masters",
    )
    result = str(t)
    assert result.startswith("@mastersthesis{")


def test_software_str():
    s = Software(
        author=["Dev, Jane"],
        title="my-tool",
        year=2024,
        version="1.0.0",
    )
    result = str(s)
    assert result.startswith("@software{")
    assert "version" in result


def test_article_str_with_article_number():
    a = Article(
        author=["Smith, A"],
        title="Paper",
        journal="J",
        year=2024,
        volume=1,
        article_number="e123",
        note="A note",
    )
    result = str(a)
    assert "article_number" in result
    assert "e123" in result
    assert "note" in result


def test_book_str_all_optional_fields():
    b = Book(
        author=["Knuth, Donald"],
        title="TAOCP",
        publisher="Addison-Wesley",
        year=1997,
        edition="3rd",
        editor=["Smith, Jane"],
        doi="10.1234/book",
        url="https://example.com",
        note="Classic text",
    )
    result = str(b)
    assert result.startswith("@book{")
    assert "edition" in result
    assert "editor" in result
    assert "Smith, Jane" in result
    assert "doi" in result
    assert "url" in result
    assert "note" in result


def test_inproceedings_str_all_optional_fields():
    ip = InProceedings(
        author=["Doe, John"],
        title="A Paper",
        booktitle="Proceedings of Foo",
        year=2023,
        pages="1--10",
        publisher="ACM",
        editor=["Chair, Ed"],
        doi="10.1234/conf",
        url="https://example.com",
        note="Oral presentation",
    )
    result = str(ip)
    assert result.startswith("@inproceedings{")
    assert "pages" in result
    assert "publisher" in result
    assert "editor" in result
    assert "doi" in result
    assert "url" in result
    assert "note" in result


def test_techreport_str_all_optional_fields():
    tr = TechReport(
        author=["Turing, Alan"],
        title="On Computable Numbers",
        institution="Cambridge",
        year=1936,
        number="TR-42",
        doi="10.1234/tr",
        url="https://example.com",
        note="Historic",
    )
    result = str(tr)
    assert result.startswith("@techreport{")
    assert "number" in result
    assert "doi" in result
    assert "url" in result
    assert "note" in result


def test_software_str_all_optional_fields():
    s = Software(
        author=["Dev, Jane"],
        title="my-tool",
        year=2024,
        publisher="GitHub",
        version="1.0.0",
        license="MIT",
        doi="10.1234/sw",
        url="https://github.com/example",
        note="Beta release",
    )
    result = str(s)
    assert result.startswith("@software{")
    assert "publisher" in result
    assert "version" in result
    assert "license" in result
    assert "doi" in result
    assert "note" in result


def test_misc_str_omits_none_fields():
    m = Misc(
        author=["Smith, A"],
        title="Something",
        year=2024,
    )
    result = str(m)
    assert "doi" not in result
    assert "url" not in result
    assert "note" not in result


# ── __repr__ ─────────────────────────────────────────────────────────────


def test_article_repr_omits_auto_key():
    a = Article(
        author=["Smith, A"],
        title="Paper",
        year=2024,
        journal="J",
        volume=1,
        pages="1",
    )
    r = repr(a)
    assert r.startswith("Article(")
    assert "key=" not in r


def test_article_repr_includes_explicit_key():
    a = Article(
        author=["Smith, A"],
        title="Paper",
        year=2024,
        journal="J",
        volume=1,
        pages="1",
        key="custom.key",
    )
    r = repr(a)
    assert "key='custom.key'" in r


def test_repr_round_trip():
    a = Article(
        author=["Huttley, Gavin", "Caley, Katherine"],
        title="diverse-seq",
        journal="JOSS",
        year=2025,
        volume=10,
        pages="7765",
        doi="10.21105/joss.07765",
    )
    r = repr(a)
    assert "Article(" in r
    assert "author=" in r
    assert "title=" in r
    assert "journal=" in r


def test_article_repr_with_article_number_and_number():
    a = Article(
        author=["Smith, A"],
        title="Paper",
        journal="J",
        year=2024,
        volume=1,
        article_number="e42",
        number=3,
        url="https://example.com",
        note="See also v2",
    )
    r = repr(a)
    assert "article_number='e42'" in r
    assert "number=3" in r
    assert "url=" in r
    assert "note=" in r


def test_book_repr_all_optional_fields():
    b = Book(
        author=["Knuth, Donald"],
        title="TAOCP",
        publisher="Addison-Wesley",
        year=1997,
        edition="3rd",
        editor=["Smith, Jane"],
        doi="10.1234/book",
    )
    r = repr(b)
    assert r.startswith("Book(")
    assert "edition=" in r
    assert "editor=" in r
    assert "doi=" in r


def test_inproceedings_repr_all_optional_fields():
    ip = InProceedings(
        author=["Doe, John"],
        title="A Paper",
        booktitle="Proceedings of Foo",
        year=2023,
        pages="1--10",
        publisher="ACM",
        editor=["Chair, Ed"],
    )
    r = repr(ip)
    assert r.startswith("InProceedings(")
    assert "pages=" in r
    assert "publisher=" in r
    assert "editor=" in r


def test_techreport_repr_with_number():
    tr = TechReport(
        author=["Turing, Alan"],
        title="On Computable Numbers",
        institution="Cambridge",
        year=1936,
        number="TR-42",
    )
    r = repr(tr)
    assert r.startswith("TechReport(")
    assert "number=" in r


def test_thesis_repr_with_optional_fields():
    t = Thesis(
        author=["Student, Alice"],
        title="My Thesis",
        year=2022,
        school="MIT",
        thesis_type="phd",
        doi="10.1234/thesis",
        url="https://example.com",
        note="Summa cum laude",
    )
    r = repr(t)
    assert r.startswith("Thesis(")
    assert "doi=" in r
    assert "url=" in r
    assert "note=" in r


def test_software_repr_all_optional_fields():
    s = Software(
        author=["Dev, Jane"],
        title="my-tool",
        year=2024,
        publisher="GitHub",
        version="1.0.0",
        license="MIT",
    )
    r = repr(s)
    assert r.startswith("Software(")
    assert "publisher=" in r
    assert "version=" in r
    assert "license=" in r


def test_repr_omits_none_optional_fields():
    m = Misc(
        author=["Smith, A"],
        title="Thing",
        year=2024,
    )
    r = repr(m)
    assert "doi=" not in r
    assert "url=" not in r
    assert "note=" not in r


# ── summary() ────────────────────────────────────────────────────────────


def test_summary_multiple_authors():
    a = Article(
        author=["Huttley, Gavin", "Caley, Katherine", "McArthur, Robert"],
        title="diverse-seq: an application for alignment-free selecting and clustering biological sequences",
        journal="JOSS",
        year=2025,
        volume=10,
        pages="7765",
        app="diverse-seq",
    )
    app_name, citation_str = a.summary()
    assert app_name == "diverse-seq"
    assert citation_str.startswith("Huttley et al. 2025")
    assert "\u2026" in citation_str


def test_summary_single_author():
    s = Software(
        author=["Smith, Jane"],
        title="my-cogent3-plugin",
        year=2024,
        app="my-plugin",
    )
    app_name, citation_str = s.summary()
    assert app_name == "my-plugin"
    assert citation_str.startswith("Smith 2024")


def test_summary_no_app():
    m = Misc(
        author=["Smith, A"],
        title="Something",
        year=2024,
    )
    app_name, _citation_str = m.summary()
    assert app_name == ""


def test_summary_long_title_truncated():
    m = Misc(
        author=["Smith, A"],
        title="A" * 60,
        year=2024,
    )
    _, citation_str = m.summary()
    assert citation_str.endswith("\u2026")


def test_summary_short_title_not_truncated():
    m = Misc(
        author=["Smith, A"],
        title="Short title",
        year=2024,
    )
    _, citation_str = m.summary()
    assert "\u2026" not in citation_str


# ── JSON round-trip ──────────────────────────────────────────────────────


def _make_all_types() -> list[CitationBase]:
    """Return one instance of each entry type with distinctive fields."""
    return [
        Article(
            author=["Huttley, Gavin"],
            title="diverse-seq",
            year=2025,
            journal="JOSS",
            volume=10,
            pages="7765",
            key="custom.key",
            app="diverse-seq",
        ),
        Book(
            author=["Knuth, Donald"],
            title="TAOCP",
            year=1997,
            publisher="Addison-Wesley",
            edition="3rd",
        ),
        InProceedings(
            author=["Doe, John"],
            title="A Paper",
            year=2023,
            booktitle="Proceedings",
            pages="1--10",
        ),
        TechReport(
            author=["Turing, Alan"],
            title="On Computable Numbers",
            year=1936,
            institution="Cambridge",
            number="TR-42",
        ),
        Thesis(
            author=["Student, Alice"],
            title="My Thesis",
            year=2022,
            school="MIT",
            thesis_type="phd",
        ),
        Software(
            author=["Dev, Jane"],
            title="my-tool",
            year=2024,
            version="1.0.0",
        ),
        Misc(
            author=["Smith, A"],
            title="Something",
            year=2024,
            doi="10.1234/misc",
        ),
    ]


@pytest.mark.parametrize("citation", _make_all_types(), ids=lambda c: type(c).__name__)
def test_to_dict_from_dict_round_trip(citation: CitationBase) -> None:
    d = citation.to_dict()
    restored = CitationBase.from_dict(d)
    assert restored == citation
    assert restored.key == citation.key
    assert restored.app == citation.app


@pytest.mark.parametrize("citation", _make_all_types(), ids=lambda c: type(c).__name__)
def test_to_dict_contains_type(citation: CitationBase) -> None:
    d = citation.to_dict()
    assert "type" in d
    assert d["type"] == type(citation).__name__


def test_from_dict_unknown_type() -> None:
    with pytest.raises(ValueError, match="unknown citation type"):
        CitationBase.from_dict(
            {"type": "Nonexistent", "author": ["A"], "title": "T", "year": 2024}
        )


def test_from_dict_missing_type() -> None:
    with pytest.raises(ValueError, match="missing required 'type' key"):
        CitationBase.from_dict({"author": ["A"], "title": "T", "year": 2024})


def test_to_jsons_from_jsons_mixed_types() -> None:
    originals = _make_all_types()
    json_str = to_jsons(originals)
    restored = from_jsons(json_str)
    assert len(restored) == len(originals)
    for orig, rest in zip(originals, restored, strict=True):
        assert type(rest) is type(orig)
        assert rest == orig
        assert rest.key == orig.key
        assert rest.app == orig.app


def test_write_json_load_json(tmp_path: pathlib.Path) -> None:
    originals = _make_all_types()
    path = tmp_path / "citations.json"
    write_json(citations=originals, path=path)
    assert path.exists()
    restored = load_json(path)
    assert len(restored) == len(originals)
    for orig, rest in zip(originals, restored, strict=True):
        assert type(rest) is type(orig)
        assert rest == orig
        assert rest.key == orig.key
        assert rest.app == orig.app
