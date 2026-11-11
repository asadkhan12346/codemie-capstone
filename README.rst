Flaskr
======

The basic blog app built in the Flask `tutorial`_.

.. _tutorial: https://flask.palletsprojects.com/tutorial/


Install
-------

**Be sure to use the same version of the code as the version of the docs
you're reading.** You probably want the latest tagged version, but the
default Git version is the main branch. ::

    # clone the repository
    $ git clone https://github.com/pallets/flask
    $ cd flask
    # checkout the correct version
    $ git tag  # shows the tagged versions
    $ git checkout latest-tag-found-above
    $ cd examples/tutorial

Create a virtualenv and activate it::

    $ python3 -m venv .venv
    $ . .venv/bin/activate

Or on Windows cmd::

    $ py -3 -m venv .venv
    $ .venv\Scripts\activate.bat

Install Flaskr::

    $ pip install -e .

Or if you are using the main branch, install Flask from source before
installing Flaskr::

    $ pip install -e ../..
    $ pip install -e .


Configure
---------

When running without ``--debug`` (and outside of tests), Flaskr refuses to
start unless a ``SECRET_KEY`` is configured. A missing, blank, or ``dev``
key is rejected, because sessions signed with a predictable key can be
forged. In debug and testing mode no key is required.

Generate a random key::

    $ python -c 'import secrets; print(secrets.token_hex())'

Then provide it in one of two ways. If both are set, the environment
variable wins.

Set the ``SECRET_KEY`` environment variable::

    $ export SECRET_KEY='paste-the-generated-key-here'

Or on Windows cmd::

    > set SECRET_KEY=paste-the-generated-key-here

Or create ``instance/config.py`` containing::

    SECRET_KEY = 'paste-the-generated-key-here'


Run
---

.. code-block:: text

    $ flask --app flaskr init-db
    $ flask --app flaskr run --debug

Open http://127.0.0.1:5000 in a browser.

To run without debug mode, configure ``SECRET_KEY`` first (see
`Configure`_), then::

    $ flask --app flaskr run


Test
----

::

    $ pip install '.[test]'
    $ pytest

Run with coverage report::

    $ coverage run -m pytest
    $ coverage report
    $ coverage html  # open htmlcov/index.html in a browser
