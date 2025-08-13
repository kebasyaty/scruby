<div align="center">
  <p align="center">
    <a href="https://github.com/kebasyaty/scruby">
      <img
        height="90"
        alt="Logo"
        src="https://raw.githubusercontent.com/kebasyaty/scruby/main/assets/logo.svg">
    </a>
  </p>
  <p>
    <h1>Scruby</h1>
    <h3>A fast key-value storage library.</h3>
    <p align="center">
      <a href="https://github.com/kebasyaty/scruby/actions/workflows/test.yml" alt="Build Status"><img src="https://github.com/kebasyaty/scruby/actions/workflows/test.yml/badge.svg" alt="Build Status"></a>
      <a href="https://kebasyaty.github.io/scruby/" alt="Docs"><img src="https://img.shields.io/badge/docs-available-brightgreen.svg" alt="Docs"></a>
      <a href="https://pypi.python.org/pypi/scruby/" alt="PyPI pyversions"><img src="https://img.shields.io/pypi/pyversions/scruby.svg" alt="PyPI pyversions"></a>
      <a href="https://pypi.python.org/pypi/scruby/" alt="PyPI status"><img src="https://img.shields.io/pypi/status/scruby.svg" alt="PyPI status"></a>
      <a href="https://pypi.python.org/pypi/scruby/" alt="PyPI version fury.io"><img src="https://badge.fury.io/py/scruby.svg" alt="PyPI version fury.io"></a>
      <br>
      <a href="https://github.com/kebasyaty/scruby/issues"><img src="https://img.shields.io/github/issues/kebasyaty/scruby.svg" alt="GitHub issues"></a>
      <a href="https://pepy.tech/projects/scruby"><img src="https://static.pepy.tech/badge/scruby" alt="PyPI Downloads"></a>
      <a href="https://github.com/kebasyaty/scruby/blob/main/LICENSE" alt="GitHub license"><img src="https://img.shields.io/github/license/kebasyaty/scruby" alt="GitHub license"></a>
      <a href="https://mypy-lang.org/" alt="Types: Mypy"><img src="https://img.shields.io/badge/types-Mypy-202235.svg?color=0c7ebf" alt="Types: Mypy"></a>
      <a href="https://docs.astral.sh/ruff/" alt="Code style: Ruff"><img src="https://img.shields.io/badge/code%20style-Ruff-FDD835.svg" alt="Code style: Ruff"></a>
      <a href="https://github.com/kebasyaty/scruby" alt="PyPI implementation"><img src="https://img.shields.io/pypi/implementation/scruby" alt="PyPI implementation"></a>
      <a href="https://github.com/kebasyaty/scruby" alt="GitHub repository"><img src="https://img.shields.io/badge/--ecebeb?logo=github&logoColor=000000" alt="GitHub repository"></a>
      <br>
      <a href="https://pypi.org/project/scruby"><img src="https://img.shields.io/pypi/format/scruby" alt="Format"></a>
      <a href="https://github.com/kebasyaty/scruby"><img src="https://img.shields.io/github/languages/top/kebasyaty/scruby" alt="Top"></a>
      <a href="https://github.com/kebasyaty/scruby"><img src="https://img.shields.io/github/repo-size/kebasyaty/scruby" alt="Size"></a>
      <a href="https://github.com/kebasyaty/scruby"><img src="https://img.shields.io/github/last-commit/kebasyaty/scruby/main" alt="Last commit"></a>
      <a href="https://github.com/kebasyaty/scruby/releases/" alt="GitHub release"><img src="https://img.shields.io/github/release/kebasyaty/scruby" alt="GitHub release"></a>
    </p>
    <p align="center">
      **Scruby** is a fast key-value storage library that provides an ordered mapping from string keys to string values.
      <br>
      The library uses fractal-tree addressing.
      <br>
      The maximum size of the database is 16^32=340282366920938463463374607431768211456 branches,
      each branch can store one or more keys.
      <br>
      The value of any key can be obtained in 32 steps, thereby achieving high performance.
      <br>
      There is no need to iterate through all the keys in search of the desired value.
    </p>
  </p>
</div>

##

<p>
  <a href="https://github.com/kebasyaty/scruby" alt="Project Status">
    <img src="https://raw.githubusercontent.com/kebasyaty/scruby/v0/assets/project_status/project-status-pre-alpha.svg"
      alt="Project Status">
  </a>
</p>

## Documentation

Online browsable documentation is available at [https://kebasyaty.github.io/scruby/](https://kebasyaty.github.io/scruby/ "Documentation").

## Requirements

[View the list of requirements](https://github.com/kebasyaty/scruby/blob/v0/REQUIREMENTS.md "Requirements").

## Installation

```shell
uv add scruby
```

## Usage

[It is recommended to look at examples here](https://github.com/kebasyaty/scruby/tree/main/examples "Examples").

```python
import scruby
```

## Changelog

[View the change history](https://github.com/kebasyaty/scruby/blob/v0/CHANGELOG.md "Changelog").

## License

This project is licensed under the [MIT](https://github.com/kebasyaty/scruby/blob/main/LICENSE "MIT").
