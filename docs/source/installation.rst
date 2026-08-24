============
Installation
============

PyRCS can be installed using `uv`_ (recommended for speed, reliability and modern dependency resolution) or traditional `pip`_.

Using ``uv`` (Recommended)
==========================

`uv`_ is a fast Python package installer and project manager written in Rust.

Adding to a ``uv`` Project
---------------------------

To add the latest release of PyRCS to your existing project managed by ``uv``:

.. code-block:: console

    > uv add pyrcs

Installing in a Virtual Environment
-----------------------------------

If you are working inside an active virtual environment and wish to install PyRCS directly using ``uv pip``:

.. code-block:: console

    > uv pip install --upgrade pyrcs

To install the latest development version directly from `GitHub <https://github.com/mikeqfu/pyrcs>`_:

.. code-block:: console

    > uv pip install --upgrade git+https://github.com/mikeqfu/pyrcs.git


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
.. _`virtual environment`: https://packaging.python.org/glossary/#term-Virtual-Environment
.. _`pip install`: https://pip.pypa.io/en/stable/cli/pip_install/
.. _`pip`: https://pip.pypa.io/en/stable/cli/pip/
.. _`Python Packaging User Guide`: https://packaging.python.org/tutorials/installing-packages/