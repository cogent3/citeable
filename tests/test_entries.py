"""Tests for citation entry type construction and validation."""

import pytest

from citeable import (
    Article,
    Book,
    InProceedings,
    Misc,
    Software,
    TechReport,
    Thesis,
)

# ── Article ──────────────────────────────────────────────────────────────


def test_article_construction():
    a = Article(
        author=["Huttley, Gavin", "Caley, Katherine"],
        title="A paper",
        year=2025,
        journal="JOSS",
        volume=10,
        pages="7765",
    )
    assert a.author == ["Huttley, Gavin", "Caley, Katherine"]
    assert a.journal == "JOSS"
    assert a.volume == 10
    assert a.pages == "7765"
    assert a.key == "Huttley.2025"


def test_article_with_article_number():
    a = Article(
        author=["Smith, Jane"],
        title="Something",
        year=2024,
        journal="Nature",
        volume=1,
        article_number="e123",
    )
    assert a.article_number == "e123"
    assert a.pages is None


def test_article_advance_access():
    a = Article(
        author=["Smith, Jane"],
        title="Something",
        year=2024,
        journal="Nature",
        doi="10.1234/example",
    )
    assert a.volume is None
    assert a.pages is None
    assert a.article_number is None


def test_article_missing_journal():
    with pytest.raises(ValueError, match="Article requires 'journal'"):
        Article(
            author=["Smith, Jane"],
            title="Something",
            year=2024,
            journal=None,  # type: ignore[arg-type]
            volume=1,
            pages="1-10",
        )


def test_article_empty_authors():
    with pytest.raises(ValueError, match="at least one author"):
        Article(
            author=[],
            title="Something",
            year=2024,
            journal="Nature",
            volume=1,
            pages="1-10",
        )


# ── Book ─────────────────────────────────────────────────────────────────


def test_book_construction():
    b = Book(
        author=["Knuth, Donald"],
        title="The Art of Programming",
        year=1997,
        publisher="Addison-Wesley",
    )
    assert b.publisher == "Addison-Wesley"
    assert b.key == "Knuth.1997"


def test_book_missing_publisher():
    with pytest.raises(ValueError, match="Book requires 'publisher'"):
        Book(
            author=["Knuth, Donald"],
            title="The Art",
            year=1997,
            publisher=None,  # type: ignore[arg-type]
        )


# ── InProceedings ────────────────────────────────────────────────────────


def test_inproceedings_construction():
    ip = InProceedings(
        author=["Doe, John"],
        title="A Conference Paper",
        year=2023,
        booktitle="Proceedings of Foo",
    )
    assert ip.booktitle == "Proceedings of Foo"
    assert ip.key == "Doe.2023"


def test_inproceedings_missing_booktitle():
    with pytest.raises(ValueError, match="InProceedings requires 'booktitle'"):
        InProceedings(
            author=["Doe, John"],
            title="Paper",
            year=2023,
            booktitle=None,  # type: ignore[arg-type]
        )


# ── TechReport ───────────────────────────────────────────────────────────


def test_techreport_construction():
    tr = TechReport(
        author=["Turing, Alan"],
        title="On Computable Numbers",
        year=1936,
        institution="Cambridge",
    )
    assert tr.institution == "Cambridge"
    assert tr.key == "Turing.1936"


def test_techreport_missing_institution():
    with pytest.raises(ValueError, match="TechReport requires 'institution'"):
        TechReport(
            author=["Turing, Alan"],
            title="A Report",
            year=1936,
            institution=None,  # type: ignore[arg-type]
        )


# ── Thesis ───────────────────────────────────────────────────────────────


def test_thesis_phd():
    t = Thesis(
        author=["Student, Alice"],
        title="My Thesis",
        year=2022,
        school="MIT",
        thesis_type="phd",
    )
    assert t.thesis_type == "phd"
    assert t.school == "MIT"


def test_thesis_masters():
    t = Thesis(
        author=["Student, Bob"],
        title="My Thesis",
        year=2021,
        school="Oxford",
        thesis_type="masters",
    )
    assert t.thesis_type == "masters"


def test_thesis_invalid_type():
    with pytest.raises(ValueError, match="'phd' or 'masters'"):
        Thesis(
            author=["Student, Alice"],
            title="My Thesis",
            year=2022,
            school="MIT",
            thesis_type="bachelor",
        )


def test_thesis_missing_school():
    with pytest.raises(ValueError, match="Thesis requires 'school'"):
        Thesis(
            author=["Student, Alice"],
            title="My Thesis",
            year=2022,
            school=None,  # type: ignore[arg-type]
            thesis_type="phd",
        )


# ── Software ─────────────────────────────────────────────────────────────


def test_software_construction():
    s = Software(
        author=["Dev, Jane"],
        title="my-tool",
        year=2024,
        version="1.0.0",
        url="https://github.com/example",
    )
    assert s.version == "1.0.0"
    assert s.key == "Dev.2024"


def test_software_minimal():
    s = Software(
        author=["Dev, Jane"],
        title="my-tool",
        year=2024,
    )
    assert s.version is None
    assert s.publisher is None


# ── Misc ─────────────────────────────────────────────────────────────────


def test_misc_construction():
    m = Misc(
        author=["Author, Some"],
        title="A Misc Entry",
        year=2020,
        note="Some note",
    )
    assert m.note == "Some note"
    assert m.key == "Author.2020"


# ── Equality and hashing ────────────────────────────────────────────────


def test_equality_same_content():
    a = Article(
        author=["Smith, A"],
        title="Paper",
        year=2024,
        journal="J",
        volume=1,
        pages="1",
    )
    b = Article(
        author=["Smith, A"],
        title="Paper",
        year=2024,
        journal="J",
        volume=1,
        pages="1",
    )
    assert a == b
    assert hash(a) == hash(b)


def test_equality_excludes_key_and_app():
    a = Article(
        author=["Smith, A"],
        title="Paper",
        year=2024,
        journal="J",
        volume=1,
        pages="1",
        key="custom.key",
        app="app1",
    )
    b = Article(
        author=["Smith, A"],
        title="Paper",
        year=2024,
        journal="J",
        volume=1,
        pages="1",
        key="other.key",
        app="app2",
    )
    assert a == b
    assert hash(a) == hash(b)


def test_identity_equality():
    a = Article(
        author=["Smith, A"],
        title="Paper",
        year=2024,
        journal="J",
        volume=1,
        pages="1",
    )
    b = a
    assert a is b
    assert a == b


def test_inequality_different_content():
    a = Article(
        author=["Smith, A"],
        title="Paper 1",
        year=2024,
        journal="J",
        volume=1,
        pages="1",
    )
    b = Article(
        author=["Smith, A"],
        title="Paper 2",
        year=2024,
        journal="J",
        volume=1,
        pages="1",
    )
    assert a != b


def test_inequality_different_types():
    a = Misc(author=["Smith, A"], title="Thing", year=2024)
    b = Software(author=["Smith, A"], title="Thing", year=2024)
    assert a != b


def test_set_deduplication():
    a = Article(
        author=["Smith, A"],
        title="Paper",
        year=2024,
        journal="J",
        volume=1,
        pages="1",
    )
    b = Article(
        author=["Smith, A"],
        title="Paper",
        year=2024,
        journal="J",
        volume=1,
        pages="1",
        key="different",
    )
    assert len({a, b}) == 1


def test_author_order_matters():
    a = Article(
        author=["Smith, A", "Jones, B"],
        title="Paper",
        year=2024,
        journal="J",
        volume=1,
        pages="1",
    )
    b = Article(
        author=["Jones, B", "Smith, A"],
        title="Paper",
        year=2024,
        journal="J",
        volume=1,
        pages="1",
    )
    assert a != b


# ── key auto-generation ─────────────────────────────────────────────────


def test_key_auto_generated():
    a = Article(
        author=["Huttley, Gavin"],
        title="Paper",
        year=2025,
        journal="J",
        volume=1,
        pages="1",
    )
    assert a.key == "Huttley.2025"


def test_key_explicit():
    a = Article(
        author=["Huttley, Gavin"],
        title="Paper",
        year=2025,
        journal="J",
        volume=1,
        pages="1",
        key="custom",
    )
    assert a.key == "custom"


def test_key_from_first_last_format():
    a = Misc(author=["Gavin Huttley"], title="Paper", year=2025)
    assert a.key == "Huttley.2025"


# ── app field ────────────────────────────────────────────────────────────


def test_app_field():
    a = Article(
        author=["Smith, A"],
        title="Paper",
        year=2024,
        journal="J",
        volume=1,
        pages="1",
        app="my-plugin",
    )
    assert a.app == "my-plugin"


def test_app_default_none():
    a = Misc(author=["Smith, A"], title="Paper", year=2024)
    assert a.app is None
