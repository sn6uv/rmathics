Building rmathics from source
=============================

rmathics is written in RPython, a subset of the Python language.
It is translated and compiled by the RPython translation toolchain.


Downloading the PyPy source
---------------------------
You must first download the RPython tranlsation toolchain::

    hg clone http://bitbucket.org/pypy/pypy pypy

This clones the PyPy repository and places it into a directory named ``pypy``.


Downloading the rmathics source
-------------------------------
To download the rmathics source::

    git clone https://github.com/sn6uv/rmathics rmathics

This clones the rmathics repository and places it into a directory named ``rmathics``.

Downloading libraries
---------------------
rmathics uses the GNU multiprecision arithmetic library for it's computations.
You will need this in order to translate the source.
The installation procedure will depend on your system.

Running rmathics untranslated
-----------------------------
The simplest way to run rmathics from source is just to run the ``main.py`` file with python directly::

    python2 main.py file.m

If you get the error ``ImportError: No module named rpython.translator.tool.cbuild`` be sure to add the PyPy
source directory to your Python path::

    export PYTHONPATH=/path/to/pypy-src/

Translating rmathics
--------------------
The translator must be run with Python 2::

    python2 /path/to/pypy-src/rpython/bin/rpython --output=rmathics main.py

You can use either CPython or PyPy for this, but CPython is faster.
The translator will churn away for a couple of minutes and then make the executable ``rmathics``.
Assuming the translation was sucessful you should now be able to run rmathics::

    ./rmathics file.m
