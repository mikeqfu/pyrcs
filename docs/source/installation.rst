============
Installation
============

To install the latest release of PyRCS from `PyPI <https://pypi.org/project/pyrcs/>`_ by using `pip <https://packaging.python.org/key_projects/#pip>`_:

.. code-block:: bash

   pip install --upgrade pyrcs

To install a more recent version of PyRCS hosted on `GitHub repository <https://github.com/mikeqfu/pyrcs>`_:

.. code-block:: bash

   pip install --upgrade git+https://github.com/mikeqfu/pyrcs.git

To test if PyRCS is correctly installed, try to import the package via an interpreter shell:

.. code-block:: python

    >>> import pyrcs

    >>> pyrcs.__version__  # Check the current release

.. parsed-literal::
    The current release version is: |version|

.. note::

    - If you are using a `virtual environment <https://packaging.python.org/glossary/#term-Virtual-Environment>`_, ensure that it is activated.

    - It is recommended to add ``--upgrade`` (or ``-U``) when you use ``pip install`` (see the instruction above) so as to get the latest stable release of the package.

    - For more general instructions, check the "`Installing Packages <https://packaging.python.org/tutorials/installing-packages>`_".

    - PyRCS has not yet been tested with `Python 2 <https://docs.python.org/2/>`_. For users who have installed both `Python 2 <https://docs.python.org/2/>`_ and `Python 3 <https://docs.python.org/3/>`_, it would be recommended to replace ``pip`` with ``pip3``. But you are more than welcome to volunteer testing the package with `Python 2 <https://docs.python.org/2/>`_ and any issues should be logged/reported onto the `Issues <https://github.com/mikeqfu/pyrcs/issues>`_ page.
