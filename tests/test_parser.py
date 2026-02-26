"""Tests for from_bibtex_string parser."""

import pytest

from citeable import (
    Article,
    Book,
    InProceedings,
    Misc,
    Software,
    TechReport,
    Thesis,
    from_bibtex_string,
)


def test_parse_article():
    cite = from_bibtex_string("""
@article{Huttley.2025,
  doi       = {10.21105/joss.07765},
  url       = {https://doi.org/10.21105/joss.07765},
  year      = {2025},
  volume    = {10},
  number    = {110},
  pages     = {7765},
  author    = {Huttley, Gavin and Caley, Katherine and McArthur, Robert},
  title     = {diverse-seq},
  journal   = {Journal of Open Source Software},
}
""")
    assert isinstance(cite, Article)
    assert cite.key == "Huttley.2025"
    assert cite.author == ["Huttley, Gavin", "Caley, Katherine", "McArthur, Robert"]
    assert cite.journal == "Journal of Open Source Software"
    assert cite.volume == 10
    assert cite.number == 110
    assert cite.pages == "7765"
    assert cite.doi == "10.21105/joss.07765"


def test_parse_software_1():
    cite = from_bibtex_string("""@software{cogent3,
  title        = {{cogent3}: making sense of sequence},
  author       = {Huttley, Gavin and Caley, Katherine and Fotovat, Nabi and Ma, Stephen Ka-Wah and Koh, Moses and Morris, Richard and McArthur, Robert and McDonald, Daniel and Jaya, Fred and Maxwell, Peter and Martini, James and La, Thomas and Lang, Yapeng},
  year         = 2025,
  month        = jul,
  doi          = {10.5281/zenodo.16519079},
  urldate      = {2025-08-02},
  howpublished = {Zenodo}
}
""")
    assert isinstance(cite, Software)


def test_parse_book():
    cite = from_bibtex_string("""
@book{Knuth.1997,
  author    = {Knuth, Donald},
  title     = {The Art of Computer Programming},
  publisher = {Addison-Wesley},
  year      = {1997},
  edition   = {3rd},
}
""")
    assert isinstance(cite, Book)
    assert cite.publisher == "Addison-Wesley"
    assert cite.edition == "3rd"


def test_parse_inproceedings():
    cite = from_bibtex_string("""
@inproceedings{Doe.2023,
  author    = {Doe, John},
  title     = {A Paper},
  booktitle = {Proceedings of Foo},
  year      = {2023},
  pages     = {1--10},
}
""")
    assert isinstance(cite, InProceedings)
    assert cite.booktitle == "Proceedings of Foo"
    assert cite.pages == "1--10"


def test_parse_techreport():
    cite = from_bibtex_string("""
@techreport{Turing.1936,
  author      = {Turing, Alan},
  title       = {On Computable Numbers},
  institution = {Cambridge},
  year        = {1936},
  number      = {TR-42},
}
""")
    assert isinstance(cite, TechReport)
    assert cite.institution == "Cambridge"
    assert cite.number == "TR-42"


def test_parse_phdthesis():
    cite = from_bibtex_string("""
@phdthesis{Student.2022,
  author = {Student, Alice},
  title  = {My Thesis},
  school = {MIT},
  year   = {2022},
}
""")
    assert isinstance(cite, Thesis)
    assert cite.thesis_type == "phd"
    assert cite.school == "MIT"


def test_parse_mastersthesis():
    cite = from_bibtex_string("""
@mastersthesis{Student.2021,
  author = {Student, Bob},
  title  = {My Thesis},
  school = {Oxford},
  year   = {2021},
}
""")
    assert isinstance(cite, Thesis)
    assert cite.thesis_type == "masters"


def test_parse_software():
    cite = from_bibtex_string("""
@software{Dev.2024,
  author    = {Dev, Jane},
  title     = {my-tool},
  year      = {2024},
  version   = {1.0.0},
  url       = {https://github.com/example},
}
""")
    assert isinstance(cite, Software)
    assert cite.version == "1.0.0"


def test_parse_misc():
    cite = from_bibtex_string("""
@misc{Author.2020,
  author = {Author, Some},
  title  = {A Misc Entry},
  year   = {2020},
  note   = {Some note},
}
""")
    assert isinstance(cite, Misc)
    assert cite.note == "Some note"


def test_parse_author_normalisation():
    cite = from_bibtex_string("""
@misc{Smith.2024,
  author = {John Smith and Jane Doe},
  title  = {A Paper},
  year   = {2024},
}
""")
    assert cite.author == ["Smith, John", "Doe, Jane"]


def test_parse_single_name_author():
    """Single-name authors (e.g. mononyms) are kept as-is."""
    cite = from_bibtex_string("""
@misc{Aristotle.2024,
  author = {Aristotle},
  title  = {Metaphysics},
  year   = {2024},
}
""")
    assert cite.author == ["Aristotle"]


def test_parse_single_name_among_multiple_authors():
    cite = from_bibtex_string("""
@misc{Plato.2024,
  author = {Plato and Jane Smith},
  title  = {Dialogues},
  year   = {2024},
}
""")
    assert cite.author == ["Plato", "Smith, Jane"]


def test_parse_preserves_cite_key():
    cite = from_bibtex_string("""
@misc{my_custom_key,
  author = {Smith, John},
  title  = {A Paper},
  year   = {2024},
}
""")
    assert cite.key == "my_custom_key"


def test_parse_article_with_article_number():
    cite = from_bibtex_string("""
@article{Smith.2024,
  author         = {Smith, John},
  title          = {A Paper},
  journal        = {Nature},
  year           = {2024},
  volume         = {1},
  article_number = {e42},
}
""")
    assert isinstance(cite, Article)
    assert cite.article_number == "e42"


def test_parse_book_with_editor():
    cite = from_bibtex_string("""
@book{Knuth.1997,
  author    = {Knuth, Donald},
  title     = {TAOCP},
  publisher = {Addison-Wesley},
  year      = {1997},
  editor    = {Smith, Jane and Doe, John},
}
""")
    assert isinstance(cite, Book)
    assert cite.editor == ["Smith, Jane", "Doe, John"]


def test_parse_inproceedings_with_publisher_and_editor():
    cite = from_bibtex_string("""
@inproceedings{Doe.2023,
  author    = {Doe, John},
  title     = {A Paper},
  booktitle = {Proceedings of Foo},
  year      = {2023},
  publisher = {ACM},
  editor    = {Chair, Ed},
}
""")
    assert isinstance(cite, InProceedings)
    assert cite.publisher == "ACM"
    assert cite.editor == ["Chair, Ed"]


def test_parse_unsupported_type():
    with pytest.raises(ValueError, match="Unsupported BibTeX entry type"):
        from_bibtex_string("""
@proceedings{Foo.2024,
  author = {Smith, John},
  title  = {A Paper},
  year   = {2024},
}
""")


def test_parse_no_entry():
    with pytest.raises(ValueError, match="No BibTeX entry found"):
        from_bibtex_string("not a bibtex string")


def test_parse_multiple_entries():
    with pytest.raises(ValueError, match="Multiple BibTeX entries"):
        from_bibtex_string("""
@misc{A.2024,
  author = {A, B},
  title  = {First},
  year   = {2024},
}
@misc{C.2024,
  author = {C, D},
  title  = {Second},
  year   = {2024},
}
""")
