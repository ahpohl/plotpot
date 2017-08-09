Software Copyright 2014 Alexander Pohl
All rights reserved. Use at your own risk.

***************************** install from source ******************************

python setup.py sdist --format zip

***************************** arbin.py *****************************************

This python script processes potentiostat data, generates plots on screen and 
saves data, figures and statistics for later use. It automatically creates a 
journal file arbin.cfg for a permanent record of processed batteries including
the mass, theoretical capacity, electrode area and thickness if provided.

The location of the journal file is per default where arbin.py is located.
The path of arbin.cfg can be changed by setting the ARBIN_CFG_PATH environment
varible. To set the location to the user's home directory,

on Windows 7/8:

go to Control Panel -> User Accounts -> Change my environment variables -> New
to set variables for the current user which does not have administrative rights
search for "environment", click on edit environment variables for your account,
click on new button in the top half of the window.

Variable name: ARBIN_CFG_PATH
Variable value: %USERPROFILE% (in the profile directory C:\Users\USER)

on Linux (bash):

export ARBIN_CFG_PATH = $HOME on terminal
or set permanently in .bashrc file

$ arbin.py -h
usage: arbin.py [-h] [options] filename

The script plots data from Arbin (*.res), Biologic (*.mpt), Ivium (*.idf)
and Gamry (*.DTA) potentiostats. It has the capability to select cycles
to be plotted and save images of the plots in PNG format. The results can
be exported in csv format for plotting in external programs like Origin
or Excel. Cycles can be split into separate files using the --zip option.

positional arguments:
  filename              Name of data file

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -q, --quiet           do not show plots
  -v, --verbose         be more verbose
  -b, --counter         use Biologic counter electrode potential
  -e, --export          export data, statistics and figures
  -f, --force           overwrite sqlite file if up to date

plot arguments:
  -p PLOT, --plot PLOT  select plots, [4-5,7,]{1}
  -o {1,2,3,4}, --smooth {1,2,3,4}
                        smooth level {1}
  -c CYCLES, --cycles CYCLES
                        select cycles, [1,]5
  -t TIME, --time TIME  select time [h], [0,]8
  -d DATA, --data DATA  select data points, [1,]100

arguments for arbin.cfg database:
  --journal             select journal table
  --config              select config table
  --delete DELETE       delete row
  --insert              insert row

explanation of the --plot option:
  1   Voltage vs. specific capacity
  2   Voltage + current vs. time
  3   Auxiliary channel vs. time
  4   Specific capacity [mAh/g]
  5   Specific energy [Wh/kg]
  6   Volumetric energy [Wh/L]
  7   Coulombic efficiency
  8   Mean voltages and hysteresis
  9   Voltammogram I vs. V
  10  dQ/dV
  11  C-rate
  12  Specific current density [mA/g]
  13  Current density [mA/cm^2]
  
For example to get a plot of the galvanostatic profile (plot 1):

$ arbin.py NMC_coincell_08.res

INFO: Imported 168424 records in 6.35 seconds; 26528 records per sec.
INFO: Creating new record in arbin.cfg.
Please give mass in [mg]: 14.3

To list the records stored in arbin.cfg use the journal option. The comment
field is automatically carried over from the Arbin res file.

$ arbin.py --journal

+----+---------------------+-----------+-----------+-----------+-------------+-
| id | file name           | mass [mg] | C [mAh/g] | file size | data points | 
+----+---------------------+-----------+-----------+-----------+-------------+-
|  1 | NMC_coincell_08.res |     14.30 |      0.00 |  19472384 |      168424 | 
+----+---------------------+-----------+-----------+-----------+-------------+-
