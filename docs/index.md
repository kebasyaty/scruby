<div align="center">
  <p align="center">
    <a href="https://github.com/kebasyaty/scruby">
      <img
        id="logo"
        alt="Logo"
        src="https://raw.githubusercontent.com/kebasyaty/scruby/v4/assets/logo.png">
    </a>
  </p>
  <p>
    <h3>Asynchronous library for building and managing a hybrid database,<br>by scheme of key-value.</h3>
    <p align="center">
      <a href="https://github.com/kebasyaty/scruby/actions/workflows/test.yml" alt="Build Status"><img src="https://github.com/kebasyaty/scruby/actions/workflows/test.yml/badge.svg" alt="Build Status"></a>
      <a href="https://kebasyaty.github.io/scruby/" alt="Docs"><img src="https://img.shields.io/badge/docs-available-brightgreen.svg" alt="Docs"></a>
      <a href="https://pypi.python.org/pypi/scruby/" alt="PyPI pyversions"><img src="https://img.shields.io/pypi/pyversions/scruby.svg" alt="PyPI pyversions"></a>
      <a href="https://pypi.python.org/pypi/scruby/" alt="PyPI status"><img src="https://img.shields.io/pypi/status/scruby.svg" alt="PyPI status"></a>
      <a href="https://pypi.python.org/pypi/scruby/" alt="PyPI version fury.io"><img src="https://badge.fury.io/py/scruby.svg" alt="PyPI version fury.io"></a>
      <br>
      <a href="https://pyrefly.org/" alt="Types: Pyrefly"><img src="https://img.shields.io/badge/types-Pyrefly-FFB74D.svg" alt="Types: Pyrefly"></a>
      <a href="https://docs.astral.sh/ruff/" alt="Code style: Ruff"><img src="https://img.shields.io/badge/code%20style-Ruff-FDD835.svg" alt="Code style: Ruff"></a>
      <a href="https://pypi.org/project/scruby"><img src="https://img.shields.io/pypi/format/scruby" alt="Format"></a>
      <a href="https://pepy.tech/projects/scruby"><img src="https://static.pepy.tech/badge/scruby" alt="PyPI Downloads"></a>
      <a href="https://github.com/kebasyaty/scruby/blob/v4/MIT-LICENSE" alt="License: MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
      <a href="https://github.com/kebasyaty/scruby/blob/v4/GPL-3.0-LICENSE" alt="License: GPL v3"><img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="License: GPL v3"></a>
    </p>
  </p>
</div>

<hr>

<p>
  The library uses fractal-tree addressing and<br>
  the search for documents based on the effect of a quantum loop.
  <br>
  <br>
  The size of each collection is 16|256|4294967296 branches,<br>
  each branch can store one or more keys.
  <br>
  <br>
  The value of any key in collection can be obtained in 1-8 steps,<br>
  thereby achieving high performance.
  <br>
  <br>
  The effectiveness of the search for documents based on a quantum loop,<br>
  requires a large number of processor threads.
</p>

<hr>

<img src="https://raw.githubusercontent.com/kebasyaty/scruby/v4/assets/attention.svg" alt="Attention">
<p>
  <b>Version 4.0</b>
  <br>
  All reasons that could lead to unrealistic production requirements have been eliminated.
  <br>
  Now uses `aiodbm` to work with documents on the file system.
  <br>
  The principle of creating custom tasks has been updated.
  <br>
  <a href="https://kebasyaty.github.io/scruby/latest/pages/usage/" alt="See documentation">See documentation.</a>
</p>

<br>
<br>
<br>

<p>
  <b>Parameter `Scruby.run(hash_reduce_left = 7)`:</b>
  <br>
  7 = 16 branches in collection (default) -> Docs: ~16000+, RAM: 2G+, CPU: 2+ (for development).
  <br>
  6 = 256 branches in collection -> Docs: ~256000+, RAM: 2G+, CPU: 2+ (for small projects).
  <br>
  0 = 4294967296 branches in collection -> Docs: ~4,294967296×10¹²+, RAM: 2G+, CPU: 2+ (only operations with keys are available).
  <br>
  <br>
  <b>If you notice the production server slowing down,</b><br>
  <b>you will need to add RAM and CPU.</b>
</p>

<hr>

[![List of plugins](https://raw.githubusercontent.com/kebasyaty/scruby/v4/assets/links/plugins.svg "List of plugins")](https://github.com/kebasyaty/scruby/blob/v4/PLUGINS.md "List of plugins")

[![Requirements](https://raw.githubusercontent.com/kebasyaty/scruby/v4/assets/links/requirements.svg "Requirements")](https://github.com/kebasyaty/scruby/blob/v4/REQUIREMENTS.md "Requirements")

[![Changelog](https://raw.githubusercontent.com/kebasyaty/scruby/v4/assets/links/changelog.svg "Changelog")](https://github.com/kebasyaty/scruby/blob/v4/CHANGELOG.md "Changelog")

[![MIT](https://raw.githubusercontent.com/kebasyaty/scruby/v4/assets/links/mit.svg "MIT")](https://github.com/kebasyaty/scruby/blob/v4/MIT-LICENSE "MIT")

[![GPL-3.0](https://raw.githubusercontent.com/kebasyaty/scruby/v4/assets/links/gpl-3.0-or-later.svg "GPL-3.0")](https://github.com/kebasyaty/scruby/blob/v4/GPL-3.0-LICENSE "GPL-3.0")
