============
Installation
============

If you are using a `virtualenv <https://packaging.python.org/key_projects/#virtualenv>`_, ensure that the virtualenv is activated.

To install the latest release of `pyrcs <https://github.com/mikeqfu/pyrcs>`_ at `PyPI <https://pypi.org/project/pyrcs/>`_ via `pip <https://packaging.python.org/key_projects/#pip>`_ on Windows Command Prompt (CMD) or Linux/Unix terminal.

.. code-block:: bash

   pip install -U pyrcs

If you would like to try the more recent version under development, install it from GitHub

.. code-block:: bash

   pip install git+https://github.com/mikeqfu/pyrcs.git

To test if pyrcs is correctly installed, try importing the package from an interpreter shell:

.. parsed-literal::

    >>> import pyrcs
    >>> pyrcs.__version__  # Check the current release
    |version|

.. note::

    - To ensure you get the most recent version, it is always recommended to add ``-U`` (or ``--upgrade``) to ``pip install``.
    - `pyrcs <https://github.com/mikeqfu/pyrcs>`_ has not yet been tested with Python 2. For users who have installed both Python 2 and 3, it would be recommended to replace ``pip`` with ``pip3``. But you are more than welcome to volunteer testing the package with Python 2 and any issues should be logged/reported onto the web page of "`Issues <https://github.com/mikeqfu/pyrcs/issues>`_".
    - For more general instructions, check the web page of "`Installing Packages <https://packaging.python.org/tutorials/installing-packages>`_".
