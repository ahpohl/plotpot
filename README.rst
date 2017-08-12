Plotpot
=======

Plotpot is a Python module that plots potentiostatic data automatically
imported with `Convpot <https://github.com/ahpohl/convpot>`__. It keeps
a journal with meta information such as mass of active material,
capacity etc. for later use.

Getting Started
---------------

Prerequisites
~~~~~~~~~~~~~

Plotpot is based on the following software:

-  `Convpot <https://github.com/ahpohl/convpot>`__
-  `NumPy <http://www.numpy.org/>`__
-  `Matplotlib <https://matplotlib.org/>`__

To get the Python environment running under Windows I recommend to use a
scientific Python distribution such as
`Anaconda <https://www.continuum.io/downloads>`__ or `Enthought
Canopy <https://www.enthought.com/products/canopy/>`__, which include 
a precompiled version of NumPy and Matplotlib.

Installing
~~~~~~~~~~

To install Plotpot follow these steps (tested under Windows 7 64 bit as
a normal user):

-  Download and install the `latest
   Convpot <https://github.com/ahpohl/convpot/releases/latest>`__
   package. During installation choose to add Convpot to the PATH of the
   current user.
-  Download and install
   `Anaconda <https://www.continuum.io/downloads>`__. Choose the Python
   3 64 bit version and install "Just for me".
-  Update Anaconda. Open an "Anaconda Prompt" and type:

   ::

       conda update conda
       conda update anaconda

-  Create a new virtual Python environment just for running Plotpot:

   ::

       conda create -n plotpot-env numpy matplotlib
       activate plotpot-env

-  Download and install Plotpot by typing:

   ::

       pip install plotpot

If all goes well you should be able to type ``plotpot`` and get a
usage message without errors about missing packages.

Usage
-----

Plotpot has the ability to export the raw data in `csv
format <https://en.wikipedia.org/wiki/Comma-separated_values>`__ for
further processing with e.g. `Microcal
Origin <http://www.originlab.com/>`__ or similar software.

Single file
~~~~~~~~~~~

Command-line Options
~~~~~~~~~~~~~~~~~~~~

-  **--help or -h** - show convpot help
-  **--version or -V** - show the version header
-  **--verbose or -v** - print verbose output, can be given multiple
   times to increase verbosity
-  **--info or -i** - display supported instruments
-  **--timer** - benchmark the program run time, useful for very large
   files
-  **--output FILE** - give alternative output filename. The default is
   the name of the first input file
-  **--merge FILE** - a file with filenames to merge one by line. A "!"
   denotes a comment.
-  **--smooth LEVEL** - smooth current and voltage data (level 1-4).
   Useful for dQ/dV plots which show artefacts due to noise.

Authors
-------

-  **Alexander Pohl** - *Initial work*

See also the list of
`CONTRIBUTORS <https://github.com/ahpohl/convpot/blob/master/CONTRIBUTORS.md>`__
who participated in this project.

Changelog
---------

All notable changes and releases are documented in the
`CHANGELOG <https://github.com/ahpohl/convpot/blob/master/CHANGELOG.md>`__.

License
-------

This project is licensed under the MIT license - see the
`LICENSE <LICENSE>`__ file for details