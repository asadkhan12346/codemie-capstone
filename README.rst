Flaskr
======

The basic blog app built in the Flask `tutorial`_.

.. _tutorial: https://flask.palletsprojects.com/tutorial/


Install
-------

**Be sure to use the same version of the code as the version of the docs
you're reading.** You probably want the latest tagged version, but the
default Git version is the main branch.

The original upstream tutorial instructions reference cloning
``pallets/flask``. For this repository (``asadkhan12346/codemie-capstone``),
clone this repository instead.

Quickstart (this repo)
----------------------

Clone the repository and install in editable mode::

    $ git clone https://github.com/asadkhan12346/codemie-capstone.git
    $ cd codemie-capstone

Create a virtualenv and activate it::

    $ python3 -m venv .venv
    $ . .venv/bin/activate

Or on Windows cmd::

    $ py -3 -m venv .venv
    $ .venv\Scripts\activate.bat

Install Flaskr::

    $ pip install -e .


Configure
---------

SECRET_KEY (required for non-debug / non-testing)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For development (debug/testing), Flask can generate a fallback key. For any
non-debug and non-testing run you must set a strong ``SECRET_KEY`` (used to
securely sign cookies and other data).

Generate a strong random key (example)::

    $ python -c "import secrets; print(secrets.token_hex(32))"

Set ``SECRET_KEY`` using one of the following (do not hardcode real secrets in
the repository):

1) Environment variable (recommended for deployments)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On macOS/Linux::

    $ export SECRET_KEY="your-generated-secret"

On Windows PowerShell::

    PS> $env:SECRET_KEY="your-generated-secret"

2) Instance config (local development convenience)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create ``instance/config.py`` and define the key::

    SECRET_KEY = "your-generated-secret"

**Do not commit secrets.** Keep ``instance/config.py`` out of version control.


Run
---

Initialize the database, then run the development server::

    $ flask --app flaskr init-db
    $ flask --app flaskr run --debug

Open http://127.0.0.1:5000 in a browser.

For non-development runs, omit ``--debug`` and ensure ``SECRET_KEY`` is set.


Test
----

Unit tests (pytest)
~~~~~~~~~~~~~~~~~~~

::

    $ pip install '.[test]'
    $ pytest

Run with coverage report::

    $ coverage run -m pytest
    $ coverage report
    $ coverage html  # open htmlcov/index.html in a browser


E2E / QA
--------

This repo may include end-to-end (E2E) tests (Playwright) and Gherkin feature
files referenced by PR #5:

- ``tests/features`` (Gherkin feature specs)
- ``tests/e2e`` (Playwright-driven E2E tests)

Environment variables used by E2E:

- ``BASE_URL``: base URL of the running app (for example,
  ``http://127.0.0.1:5000``).
- ``DATABASE``: path to the database file used for E2E runs (set as needed per
  the PR #5 notes / test configuration).

To run E2E tests, start the app (in a separate terminal), then run the E2E test
command provided by the repository's test configuration.

If Playwright (and any related E2E tooling) is not declared in
``pyproject.toml`` dependencies yet, E2E requirements are **Pending** until
PR #5 merges.


Build
-----

This repository uses the ``flit_core`` PEP 517 build backend (see
``pyproject.toml``).

If build tooling is available in your environment, you can build with either::

    $ python -m build

or::

    $ flit build

If build tooling is not available (or not declared in the repository's
dependencies), build instructions are **Pending**.


Deploy
------

Deployment scripts and platform-specific configuration are **Pending**.

Minimal production guidance:

- Set a strong ``SECRET_KEY`` (environment variable or ``instance/config.py``).
- Initialize the database (``flask --app flaskr init-db``).
- Run the application behind a production WSGI server (not the Flask
  development server).
