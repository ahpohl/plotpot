Biologic 3-electrode setup (full cell)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Biologic counter electrode plot both CE and WE simultaneously in two plots
Ask meta info twice and create two separate entries in journal with
a comment full cell name one plot working electrode with _we suffix and the 
other plot with a counter electrode _ce suffix.

Print File Table
~~~~~~~~~~~~~~~~

If files have been merged, the journal command has the option to print the 
file table on sceen with details of each merged file. The -m option takes the
journal row_ID as argument. If not a merged file print an error message. Check
if merged file by reading the device column.

Convpot merge files
~~~~~~~~~~~~~~~~~~~

Add a merge command which uses Convpot to merge files. The merge command takes
a --list or -l option to give a file with names to merge. "!" denotes a comment.
After the merge command are the filenames to merge parsed into a list. The list
needs to be converted into a long string to be passed to Convpot.

Graphical user interface (GUI)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Write a graphical user interface for Plotpot, called by plotpot gui. Use as 
many methods from the Plot, Data and Journal classes as possible. Keep the 
command line program intact and let the user choose to use the gui or not.
As the gui matures, the console interface will be depreciated at some point.