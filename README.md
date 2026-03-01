# citeable 📚

*Structured BibTeX citations for cogent3 plugins.*

[![License](https://img.shields.io/pypi/l/citeable.svg)](https://github.com/cogent3/citeable/blob/main/LICENSE)
[![Coverage Status](https://coveralls.io/repos/github/GavinHuttley/citeable/badge.svg?branch=main)](https://coveralls.io/github/GavinHuttley/citeable?branch=main)
[![PyPI version](https://badge.fury.io/py/citeable.svg)](https://badge.fury.io/py/citeable)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cogent3)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![CodeQL](https://github.com/cogent3/cogent3/actions/workflows/codeql.yml/badge.svg)](https://github.com/cogent3/cogent3/actions/workflows/codeql.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/ec0f6a2dad174b04b5dcbfdae02acab7)](https://app.codacy.com/gh/cogent3/citeable/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

## Overview

`citeable` is a light-weight zero-dependency pure Python library for defining structured bibliographic citations. It is intended as a dependency of [cogent3](https://github.com/cogent3/cogent3) and of cogent3 plugin packages, enabling plugin developers to declare citations that cogent3 can assemble into a BibTeX-compatible `.bib` file to ensure users cite their work.

## Installation

```bash
pip install citeable
```

<details>
<summary>Requirements</summary>

Pure Python, no dependencies. Requires Python >= 3.11.

</details>

## Developer quick start

<!-- [[[cog
import cog
from citeable import Article

cite = Article(
    author=["Huttley, Gavin", "Caley, Katherine", "McArthur, Robert"],
    title="diverse-seq: an application for alignment-free selecting and clustering biological sequences",
    journal="Journal of Open Source Software",
    year=2025,
    volume=10,
    number=110,
    pages="7765",
    doi="10.21105/joss.07765",
    url="https://doi.org/10.21105/joss.07765",
)
cog.outl("```python")
cog.outl("from citeable import Article")
cog.outl("")
cog.outl("cite = Article(")
cog.outl('    author=["Huttley, Gavin", "Caley, Katherine", "McArthur, Robert"],')
cog.outl('    title="diverse-seq: an application for alignment-free selecting and clustering biological sequences",')
cog.outl('    journal="Journal of Open Source Software",')
cog.outl("    year=2025,")
cog.outl("    volume=10,")
cog.outl("    number=110,")
cog.outl('    pages="7765",')
cog.outl('    doi="10.21105/joss.07765",')
cog.outl('    url="https://doi.org/10.21105/joss.07765",')
cog.outl(")")
cog.outl(f"# cite.key == {cite.key!r}")
cog.outl("```")
cog.outl("")
cog.outl("```bibtex")
cog.outl(str(cite))
cog.outl("```")
]]] -->
```python
from citeable import Article

cite = Article(
    author=["Huttley, Gavin", "Caley, Katherine", "McArthur, Robert"],
    title="diverse-seq: an application for alignment-free selecting and clustering biological sequences",
    journal="Journal of Open Source Software",
    year=2025,
    volume=10,
    number=110,
    pages="7765",
    doi="10.21105/joss.07765",
    url="https://doi.org/10.21105/joss.07765",
)
# cite.key == 'Huttley.2025'
```

```bibtex
@article{Huttley.2025,
  author    = {Huttley, Gavin and Caley, Katherine and McArthur, Robert},
  title     = {diverse-seq: an application for alignment-free selecting and clustering biological sequences},
  journal   = {Journal of Open Source Software},
  year      = {2025},
  volume    = {10},
  number    = {110},
  pages     = {7765},
  doi       = {10.21105/joss.07765},
  url       = {https://doi.org/10.21105/joss.07765},
}
```
<!-- [[[end]]] -->

## Defining a citation

<details>
<summary>Constructing directly in Python (recommended)</summary>

Citations are constructed directly in Python source. Required fields are positional-or-keyword constructor arguments; optional fields are keyword-only with `None` defaults. `key` is always optional at construction -- it will be auto-generated if omitted (see [Key generation](#key-generation) below).

```python
from citeable import Article, Software

cite = Article(
    author=["Huttley, Gavin", "Caley, Katherine", "McArthur, Robert"],
    title="diverse-seq: an application for alignment-free selecting and clustering biological sequences",
    journal="Journal of Open Source Software",
    year=2025,
    volume=10,
    number=110,
    pages="7765",
    doi="10.21105/joss.07765",
)
# cite.key == "Huttley.2025"

tool_cite = Software(
    author=["Smith, Jane"],
    title="my-cogent3-plugin",
    year=2024,
    version="1.0.0",
    url="https://github.com/jsmith/my-cogent3-plugin",
)
# tool_cite.key == "Smith.2024"
```

Validation is performed at construction time. A missing required field raises `ValueError` with a message identifying the field and entry type:

```
ValueError: Article requires 'volume'; received None
```

</details>

<details>
<summary>Parsing from a BibTeX string</summary>

`from_bibtex_string` accepts a raw BibTeX string containing a single record and returns the corresponding `citeable` object. This is the intended path for developers who already have a `.bib` entry in a reference manager -- paste the raw BibTeX string directly into Python source.

```python
from citeable import from_bibtex_string

cite = from_bibtex_string("""
@article{Huttley.2025,
  doi       = {10.21105/joss.07765},
  url       = {https://doi.org/10.21105/joss.07765},
  year      = {2025},
  volume    = {10},
  number    = {110},
  pages     = {7765},
  author    = {Huttley, Gavin and Caley, Katherine and McArthur, Robert},
  title     = {diverse-seq: an application for alignment-free selecting and clustering biological sequences},
  journal   = {Journal of Open Source Software},
}
""")
```

The cite key from the BibTeX string is preserved as the `key` value. Author names in `"First Last"` format are normalised to `"Last, First"` on parse.

**Round-trip scaffolding:** use `from_bibtex_string` + `repr()` to convert a BibTeX record into a clean Python constructor call, then paste that into your source:

<!-- [[[cog
import cog
from citeable import from_bibtex_string

cite = from_bibtex_string("""
@article{Huttley.2025,
  doi       = {10.21105/joss.07765},
  url       = {https://doi.org/10.21105/joss.07765},
  year      = {2025},
  volume    = {10},
  number    = {110},
  pages     = {7765},
  author    = {Huttley, Gavin and Caley, Katherine and McArthur, Robert},
  title     = {diverse-seq: an application for alignment-free selecting and clustering biological sequences},
  journal   = {Journal of Open Source Software},
}
""")
cog.outl("```python")
cog.outl("print(repr(cite))")
cog.outl("```")
cog.outl("")
cog.outl("```python")
cog.outl(repr(cite))
cog.outl("```")
]]] -->
```python
print(repr(cite))
```

```python
Article(
    author=['Huttley, Gavin', 'Caley, Katherine', 'McArthur, Robert'],
    title='diverse-seq: an application for alignment-free selecting and clustering biological sequences',
    year=2025,
    journal='Journal of Open Source Software',
    volume=10,
    pages='7765',
    number=110,
    doi='10.21105/joss.07765',
    url='https://doi.org/10.21105/joss.07765',
)
```
<!-- [[[end]]] -->

</details>

## Supported entry types

| Class | BibTeX `@type` | Required fields (beyond common) |
|---|---|---|
| `Article` | `@article` | `journal`, `volume`, `pages` or `article_number` |
| `Book` | `@book` | `publisher` |
| `InProceedings` | `@inproceedings` | `booktitle` |
| `TechReport` | `@techreport` | `institution` |
| `Thesis` | `@phdthesis` / `@mastersthesis` | `school`, `thesis_type` |
| `Software` | `@software` | *(none)* |
| `Misc` | `@misc` | *(none)* |

All types share common fields: `author` (required), `title` (required), `year` (required), `doi`, `url`, `note`, `key`, `app`.

<details>
<summary>Field reference</summary>

### Fields common to all entry types

| Field | Required | Notes |
|---|---|---|
| `key` | No | Auto-generated if not supplied |
| `author` | Yes | List of strings in `"Surname, Given"` format |
| `title` | Yes | |
| `year` | Yes | Integer |
| `doi` | No | Recommended where available |
| `url` | No | |
| `note` | No | |
| `app` | No | Name of the cogent3 app. Not written to BibTeX output; excluded from equality and hashing. |

### `Article`

| Field | Required |
|---|---|
| `journal` | Yes |
| `volume` | Yes |
| `pages` | Yes (or `article_number`) |
| `article_number` | No |
| `number` | No -- issue number |

### `Book`

| Field | Required |
|---|---|
| `publisher` | Yes |
| `edition` | No |
| `editor` | No -- list of strings |

### `InProceedings`

| Field | Required |
|---|---|
| `booktitle` | Yes |
| `pages` | No |
| `publisher` | No |
| `editor` | No |

### `TechReport`

| Field | Required |
|---|---|
| `institution` | Yes |
| `number` | No -- report number |

### `Thesis`

| Field | Required | Notes |
|---|---|---|
| `school` | Yes | |
| `thesis_type` | Yes | `"phd"` or `"masters"` -- determines BibTeX entry type |

### `Software`

| Field | Required |
|---|---|
| `publisher` | No -- organisation or individual releasing the software |
| `version` | No -- strongly recommended |
| `license` | No |

### `Misc`

No additional required fields beyond the common set.

</details>

## Key generation

Keys are auto-generated from the first author's surname and the year, e.g. `"Huttley.2025"`:

1. Extract surname from the first author (before the first comma, or the last token)
2. Strip non-ASCII characters and spaces; title-case the result
3. Return `"{surname}.{year}"`

On collision, `assign_unique_keys` appends a lowercase letter suffix: `"Smith.2024.a"`, `"Smith.2024.b"`, etc.

A developer may supply an explicit `key` at construction time, in which case auto-generation is skipped. But note that the key attribute of a citation can be modified and cogent3 will do this if their are key conflicts.

## Working with collections

<details>
<summary>Assigning unique keys</summary>

Because citations come from multiple independent plugin developers, key collisions are expected. The function `assign_unique_keys` resolves collisions in-place across a deduplicated list:

```python
from citeable import assign_unique_keys

unique = assign_unique_keys(citations)
```

- Deduplication by value is performed first: if two objects compare as equal, only the first is retained
- Keys already unique in the deduplicated collection are left unchanged
- Collisions between distinct citations sharing a base key get a letter suffix: `"Smith.2024"` becomes `"Smith.2024.a"`, `"Smith.2024.b"`, etc.
- The function mutates surviving objects in-place and returns the deduplicated list

cogent3 calls `assign_unique_keys` when assembling a bibliography from a composed app, so plugin developers do not need to call it themselves.

</details>

<details>
<summary>Writing a .bib file</summary>

`write_bibtex` takes a list of citations and a file path, deduplicates the list, assigns unique keys, then writes the result as a valid `.bib` file:

```python
from citeable import write_bibtex

write_bibtex(citations, "bibliography.bib")
```

For cases where only the string is needed:

```python
unique = assign_unique_keys(citations)
bib_string = "\n\n".join(str(c) for c in unique)
```

</details>

## Using citeable with cogent3

The `define_app` decorator in cogent3 has an optional `cite` argument:

```python
@define_app(cite=Article(...))
class MyPlugin:
    ...
```

cogent3 collects citations across a composed app and expose a method (e.g. `app.bibliography()`) that returns a combined `.bib` string.

## Distribution guidance

Plugin developers **must** define their citation as a Python object in their package source. This guarantees it is present after `pip install` without any special `package_data` configuration or `MANIFEST.in` entries.

The recommended pattern is a dedicated `citations.py` in the plugin package:

```
my_plugin/
    __init__.py
    citations.py   # citation objects defined here
    app.py         # @define_app(cite=MY_CITE) used here
```

`from_bibtex_string` is provided as a convenience constructor only. Either way, the result is a Python object embedded in source, not a runtime file read.

<details>
<summary>Developer setup (uv)</summary>

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

### Initial setup

```bash
uv sync
```

This creates a `.venv` and installs the package in editable mode with all dev dependencies.

### Running tests

```bash
uv run pytest
```

### Running nox (multi-version test matrix)

```bash
uv run nox
```

Nox is configured to use uv as its virtualenv backend, so it will use uv to create per-session environments.

### Formatting

```bash
uv run nox -s fmt
```

This runs `ruff check --fix-only` followed by `ruff format`.

### Other common commands

```bash
uv run mypy src/citeable --strict   # type checking
uv run ruff check .                 # linting
uv run cog -r README.md             # regenerate cog blocks
```

</details>

## Contributing

Bug reports and pull requests are welcome at https://github.com/cogent3/citeable.

## Licence

BSD-3-Clause. See [LICENSE](https://github.com/cogent3/citeable/blob/main/LICENSE).
