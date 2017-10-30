Plotpot
=======

Plotpot is a Python module that plots half and full cell potentiostatic 
data automatically imported with `Convpot <https://github.com/ahpohl/convpot>`__. 
It keeps a journal with meta information such as mass of active material,
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

Plotpot currently knows two sub-commands ``show``, ``merge`` and ``journal``. A detailed 
help of the sub-command options are printed with ``plotpot <sub-command> -h``

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
   
    plotpot show arbintest.res --plot 1,8-9
       
It is possible to give a comma separated list of plots and ranges separated with "-". If no plots are
selected, the voltage versus specific capacity (1) is plotted by default. Plotpot currently supports 
the following plot types:

1.  Specific capacity
2.  Specific capacity (circle plot) 
3.  Voltage and current
4.  Temperature
5.  dQ/dV
6.  Specific capacity [mAh/g]
7.  Volumetric capacity [Ah/L]
8.  Specific energy [Wh/kg]
9.  Volumetric energy [Wh/L] 
10.  Specific current density [mA/g]
11.  Current density [mA/cm²]
12.  C-rate 
13.  Hysteresis
14.  Coulombic efficiency

Smooth dQ/dV plot
~~~~~~~~~~~~~~~~~

Plotpot has the option to smooth the dQ/dV plot by convoluting the raw data with a Hanning window of
certain width. The smoothing strength is chosen with the level parameter ranging from 1 to 5, which 
translates to the widths of the window.

::

   plotpot show arbintest.res --cycle 2,2 --plot 5 --smooth 5

Export data
~~~~~~~~~~~

The raw data, statistics, voltage profile and battery properties are exported with

::

    plotpot show arbintest.res --export

This generates files in `csv format <https://en.wikipedia.org/wiki/Comma-separated_values>`__ for 
further processing with e.g. `Microcal Origin <http://www.originlab.com/>`__ or similar software. 
Data per cycle is packed into a zip archive and png snapshots of the plots genererated on screen are created.

Merge Files
~~~~~~~~~~~

A battery which consists of many individual data files (which is common for the Gamry instruments) can be merged together to a single data file with the "merge" sub-command.

To process multiple files

```
plotpot merge arbin-merge_1.res arbin-merge_2.res
```

Alternatively, the files to merge can be given in a text file listed one by line. Lines starting with the "!" character are ignored.

```
plotpot merge --list arbin-merge.txt
```

The output file name can be changed with the `--output` option.

The journal
~~~~~~~~~~~

On first execution, a journal file ``plotpot-journal.dat`` is created in the directory of the plotpot 
executable. The folder location can be changed by setting the ``PLOTPOT_JOURNAL`` environment variable 
to a full path as described in the `wiki <https://github.com/ahpohl/plotpot/wiki/Set-the-location-of-the-Plotpot-journal-file>`__. 

The journal file keeps a record of mass, capacity, area, volume and mass loading of the electrode. 
If plotpot is called with the same data file, you have the possibility to use the previously entered 
values or enter new ones. The content of the journal is displayed with

::
   
    plotpot journal
       
A particular entry can be removed from the journal with:

::

    plotpot journal --delete <row_ID>

The individual raw data files of a merged battery can be shown with

::

	plotpot journal --show <row_ID>
    
The journal file can be exported to a csv file:

::
	
	plotpot journal --export

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
