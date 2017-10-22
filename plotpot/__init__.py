# -*- coding: utf-8 -*-
import sys
from distutils.spawn import find_executable

# check if prerequisites are installed
try:
    from plotpot.__version__ import version
except ImportError as error:
    print("Package not installed with pip.")
    sys.exit(error)
    
try:
    import numpy as np
except ImportError as error:
    print("Please install Python Numpy from http://numpy.scipy.org/")
    sys.exit(error)
    
try:
    import matplotlib.pyplot as plt
except ImportError as error:
    print("Please install Python Matplotlib from http://matplotlib.sourceforge.net/")
    sys.exit(error)
    
convpot_program = find_executable("convpot")
if not convpot_program:
    print("Please install Convpot from https://github.com/ahpohl/convpot/")
    sys.exit()