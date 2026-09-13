============
Installation
============

PyRCS can be installed via `uv`_ (recommended for speed, reliability and modern dependency resolution), `pixi`_, traditional `pip`_ or `conda-forge`_.


Using ``uv`` (Recommended)
==========================

`uv`_ is a fast Python package installer and project manager written in Rust.

Adding to a ``uv`` project
--------------------------

To add the latest release of PyRCS to your existing project managed by `uv`_:

.. code-block:: console

    > uv add pyrcs

Installing in a virtual environment
-----------------------------------

If you are working inside an active virtual environment and wish to install PyRCS directly using ``uv pip``:

.. code-block:: console

    > uv pip install --upgrade pyrcs

To install the latest development version directly from `GitHub <https://github.com/mikeqfu/pyrcs>`_:

.. code-block:: console

    > uv pip install --upgrade git+[https://github.com/mikeqfu/pyrcs.git](https://github.com/mikeqfu/pyrcs.git)


Using ``pixi``
==============

`pixi`_ is a modern package management tool built on top of `conda-forge`_.

Adding to a ``pixi`` project
-----------------------------

To add the core PyRCS package to a workspace using `pixi`_:

.. code-block:: console

    > pixi add pyrcs

Alternatively, to install PyRCS with PyPI extras inside a `pixi`_ project:

.. code-block:: console

    > pixi add --pypi pyrcs

Installing globally
-------------------

To install PyRCS as a globally accessible tool via `pixi`_:

.. code-block:: console

    > pixi global install pyrcs


Using ``pip``
=============

If you prefer standard Python packaging tools, ensure your `virtual environment`_ is activated and use `pip install`_:

.. code-block:: console

    > pip install --upgrade pyrcs

To install the development version from GitHub:

.. code-block:: console

    > pip install --upgrade git+https://github.com/mikeqfu/pyrcs.git


.. note::

    - For general guidelines on Python virtual environments and dependency management, refer to the `Python Packaging User Guide`_.


Using ``conda`` or ``mamba``
============================

PyRCS is published on `conda-forge`_ and can be managed using `conda`_ or `mamba`_.

Installing the core package
---------------------------

To install PyRCS into an active environment using `conda`_:

.. code-block:: console

    > conda install -c conda-forge pyrcs

Or, using `mamba`_:

.. code-block:: console

    > mamba install -c conda-forge pyrcs


Verification
============

To verify the installation, import the package in a Python interpreter shell:

.. code-block:: python
    :name: cmd current version

    >>> import pyrcs
    >>> pyrcs.__version__  # Check the latest version

.. parsed-literal::
    The latest version is: |version|


.. _`uv`: https://docs.astral.sh/uv/
.. _`pixi`: https://pixi.sh/
.. _`conda-forge`: https://anaconda.org/conda-forge/pyrcs
.. _`conda`: https://docs.conda.io/
.. _`mamba`: https://mamba.readthedocs.io/
.. _`virtual environment`: https://packaging.python.org/glossary/#term-Virtual-Environment
.. _`pip install`: https://pip.pypa.io/en/stable/cli/pip_install/
.. _`pip`: https://pip.pypa.io/en/stable/cli/pip/
.. _`Python Packaging User Guide`: https://packaging.python.org/tutorials/installing-packages/
