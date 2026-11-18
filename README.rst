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
clone this repo instead.

Quickstart (this repo)
----------------------

Clone the repository and install in editable mode::

    # clone this repository
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


Configuration
-------------

SECRET_KEY (required for non-debug / non-testing)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For development, Flask can generate a fallback key, but for any non-debug and
non-testing run you must set a strong ``SECRET_KEY`` (used to securely sign
cookies and other data).

You can set ``SECRET_KEY`` in either of these ways:

1) Environment variable
^^^^^^^^^^^^^^^^^^^^^^^

Set ``SECRET_KEY`` in your environment (recommended for deployments)::

    $ export SECRET_KEY="replace-with-a-long-random-secret"

On Windows PowerShell::

    PS> $env:SECRET_KEY="replace-with-a-long-random-secret"

2) Instance config
^^^^^^^^^^^^^^^^^^

Create an instance config file at ``instance/config.py`` and define the key::

    SECRET_KEY = "replace-with-a-long-random-secret"

**Do not commit secrets.** Keep ``instance/config.py`` out of version control
and do not hardcode real keys in the repository.


Run
---

Initialize the database, then run the development server. The following line is
kept verbatim from the existing README::

    $ flask --app flaskr init-db
    $ flask --app flaskr run --debug

Open http://localhost:5000 in a browser.

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

E2E tests (Playwright) and Gherkin features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This repo includes end-to-end tests (Playwright) and Gherkin feature files as
referenced by PR #5, located under:

- ``tests/features`` (Gherkin feature specs)
- ``tests/e2e`` (Playwright-driven E2E tests)

Environment variables used by E2E:

- ``BASE_URL``: base URL of the running app. Defaults to
  ``http://localhost:5000`` if not set.
- ``DATABASE``: path to the database file used for E2E runs (set as needed per
  the PR #5 notes / test configuration).

To run E2E tests, start the app (in a separate terminal) and then run the E2E
test command provided by this repository's test configuration.


Build
-----

This repository uses the ``flit_core`` PEP 517 build backend (see
``pyproject.toml``). If the ``build`` frontend is available as a dependency in
your environment, you can build with::

    $ python -m build

If ``python -m build`` is not available in this repo's declared dependencies,
build support is **Pending** (install ``build`` manually in your environment).


Deploy
------

Deployment scripts and platform-specific configuration are **Pending**.

Generic production guidance:

- Set a strong ``SECRET_KEY`` via environment variable or ``instance/config.py``.
- Run the application behind a production WSGI server (rather than the Flask
  development server).
- Ensure the database is initialized (``flask --app flaskr init-db``) and any
  required environment variables are set before starting.