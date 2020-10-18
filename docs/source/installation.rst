============
Installation
============

To install the latest release of PyRCS at `PyPI`_ via `pip`_:

.. code-block:: bash

   pip install --upgrade pyrcs

To install the more recent version hosted directly from `GitHub repository`_:

.. code-block:: bash

   pip install --upgrade git+https://github.com/mikeqfu/pyrcs.git

To test if PyRCS is correctly installed, try importing the package via an interpreter shell:

.. code-block:: python

    >>> import pyrcs

    >>> pyrcs.__version__  # Check the current release

.. parsed-literal::
    The current release version is: |version|

.. note::

    - If using a `virtual environment`_, ensure that it is activated.

    - To ensure you get the most recent version, it is always recommended to add ``--upgrade`` (or ``-U``) to ``pip install``.

    - The package has not yet been tested with `Python 2`_. For users who have installed both Python 2 and `Python 3`_, it would be recommended to replace ``pip`` with ``pip3``. But you are more than welcome to volunteer testing the package with Python 2 and any issues should be logged/reported onto the `Issues`_ page.

    - For more general instructions, check the "`Installing Packages <https://packaging.python.org/tutorials/installing-packages>`_".


.. _`PyPI`: https://pypi.org/project/pyrcs/
.. _`pip`: https://packaging.python.org/key_projects/#pip
.. _`GitHub repository`: https://github.com/mikeqfu/pyrcs

.. _`virtual environment`: https://packaging.python.org/glossary/#term-Virtual-Environment
.. _`virtualenv`: https://packaging.python.org/key_projects/#virtualenv
.. _`Python 2`: https://docs.python.org/2/
.. _`Python 3`: https://docs.python.org/3/
.. _`Issues`: https://github.com/mikeqfu/pyrcs/issues