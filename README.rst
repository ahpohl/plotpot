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

1. Download and install the `latest
   Convpot <https://github.com/ahpohl/convpot/releases/latest>`__
   package. During installation choose to add Convpot to the PATH of the
   current user.
2. Download and install
   `Anaconda <https://www.continuum.io/downloads>`__. Choose the Python
   3 64 bit version and install "Just for me".
3. Update Anaconda. Open an "Anaconda Prompt" and type:

   ::

       conda update conda
       conda update anaconda

4. Create a new virtual Python environment just for running Plotpot:

   ::

       conda create -n plotpot-env numpy matplotlib
       activate plotpot-env

5. Download and install Plotpot by typing:

   ::

       pip install plotpot

If all goes well you should be able to type ``plotpot`` and get a
usage message without errors about missing packages.

Usage
-----

Plotpot currently knows two sub-commands ``show`` and ``journal``. A detailed help of the 
sub-command options are printed with ``plotpot <sub-command> -h``

An example plot generated with ``plotpot show arbintest.res`` looks like this:

.. image:: https://raw.githubusercontent.com/ahpohl/plotpot/master/resources/arbintest.png

Select data
~~~~~~~~~~~

By default all available data is plotted. The range can be selected by

* cycle number (``--cycles``)
* time (in hours) (``--time``)
* data points (``--data``)

For example to plot data up to cycle 10:

::

    plotpot show arbintest.res --cycles 10
    
To plot from cycle 3 to 6:

::

    plotpot show arbintest.res --cycles 3,6

Select plots
~~~~~~~~~~~~

Plots are selected with the ``--plot`` option, *e.g.*

::
   
    plotpot show arbintest.res --plot 1,4-5
       
It is possible to give a comma separated list of plots and ranges separated with "-". If no plots are selected, the voltage versus specific capacity (1) is plotted by default. Plotpot currently supports the following plot types:

1.  Voltage vs. specific capacity
2.  Voltage and current vs. time
3.  Auxiliary channel, e.g. temperature vs. time
4.  Specific capacity [mAh/g] per cycle
5.  Specific energy [Wh/kg] per cycle
6.  Volumetric energy [Wh/L] per cyclet
7.  Coulombic efficiency per cycle
8.  Mean voltages and hysteresis per cycle
9.  dQ/dV vs. voltage
10. C-rate per cycle
11. Specific current density [mA/g] per cycle
12. Current density [mA/cm²] per cycle
13. Specific capacity as charge/dischage circle

Smooth dQ/dV plot
~~~~~~~~~~~~~~~~~

Plotpot has the option to smooth the dQ/dV plot by convoluting the raw data with a Hanning window of
certain width. The smoothing strength is chosen with the level parameter ranging from 1 to 4, which 
translates to the widths of the window.

::

   plotpot show arbintest.res --cycle 2,2 --plot 9 --smooth 4

Export data
~~~~~~~~~~~

The raw data, statistics and data per cycle are exported with

::

    plotpot show arbintest.res --export

This generates files in `csv format <https://en.wikipedia.org/wiki/Comma-separated_values>`__ for further processing with e.g. `Microcal Origin <http://www.originlab.com/>`__ or similar software. Data per cycle is packed into a zip archive and png snapshots of the plots genererated on screen are created.

The journal
~~~~~~~~~~~

On first execution, a journal file ``plotpot-journal.dat`` is created in the directory of the plotpot executable. The folder location can be changed by setting the ``PLOTPOT_JOURNAL`` environment variable to a full path as described in the `wiki <https://github.com/ahpohl/plotpot/wiki/Set-the-location-of-the-Plotpot-journal-file>`__. 

The journal file keeps a record of mass, capacity, area and volume of the electrode. If plotpot is called with the same data file, you have the possibility to use the previously entered values or enter new ones. The content of the journal is displayed with

::
   
    plotpot journal
       
A particular entry can be removed from the journal with

::

    plotpot journal --delete <row_ID>

Authors
-------

-  **Alexander Pohl** - *Initial work*

See also the list of `CONTRIBUTORS <https://github.com/ahpohl/plotpot/blob/master/CONTRIBUTORS.rst>`__ who participated in this project.

Changelog
---------

All notable changes and releases are documented in the `CHANGELOG <https://github.com/ahpohl/plotpot/blob/master/CHANGELOG.rst>`__.

License
-------

This project is licensed under the MIT license - see the `LICENSE <https://github.com/ahpohl/plotpot/blob/master/LICENSE.txt>`__ file for details
