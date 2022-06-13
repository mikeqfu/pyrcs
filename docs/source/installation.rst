.. _pyrcs-installation:

============
Installation
============

To install the latest release of pyrcs from `PyPI`_ via `pip`_:

.. _`PyPI`: https://pypi.org/project/pyrcs/
.. _`pip`: https://pip.pypa.io/en/stable/cli/pip/

.. code-block:: bash

   pip install --upgrade pyrcs

To install the most recent version of pyrcs hosted on `GitHub`_:

.. _`GitHub`: https://github.com/mikeqfu/pyrcs

.. code-block:: bash

   pip install --upgrade git+https://github.com/mikeqfu/pyrcs.git


.. note::

    - If using a `virtual environment`_, make sure it is activated.
    - It is recommended to add `pip install`_ the option ``--upgrade`` (or ``-U``) to ensure that you are getting the latest stable release of the package.
    - For more general instructions on the installation of Python packages, please refer to the official guide on `Installing Packages`_.

    .. _`virtual environment`: https://packaging.python.org/glossary/#term-Virtual-Environment
    .. _`pip install`: https://pip.pypa.io/en/stable/cli/pip_install/
    .. _`Installing Packages`: https://packaging.python.org/tutorials/installing-packages/


To check whether pyrcs has been correctly installed, try to import the package via an interpreter shell:

.. code-block:: python
    :name: cmd current version

    >>> import pyrcs

    >>> pyrcs.__version__  # Check the latest version

.. parsed-literal::
    The latest version is: |version|
