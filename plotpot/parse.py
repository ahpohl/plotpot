# -*- coding: utf-8 -*-
from globals import args
import sys

# read data functions
def is_number(s):
    """This function tests if string s is a number."""
    try:
        float(s)
        return True
    except ValueError:
        return False

def range_option(option):
    """This function parses the a command line option which specifies
    a data range and returns a tuple with the interval"""
    
    errormsg_not_recognised = "Error: Option not recognised."
    
    string = option.split(',')
    if len(string) == 2:
        if is_number(string[0]) and is_number(string[1]):
            interval = (string[0],string[1])
        else:
            sys.exit(errormsg_not_recognised)
    elif len(string) == 1:
        if is_number(string[0]):
            interval = (0,string[0])
        else:
            sys.exit(errormsg_not_recognised)
    else:    
        sys.exit(errormsg_not_recognised)
        
    return interval

def plot_option():
    """This function parses the --plot option and returns a list of plots."""
    
    errormsg_not_recognised = "Error: Plot option not recognised."
    errormsg_range_error = "Error: Plot out of range."
    
    plots = []
    string_sequence = args.plot.split(',')
    for s in string_sequence:
        if is_number(s):
            plots.append(int(s))
        elif '-' in s:
            string_range = s.split('-')
            if is_number(string_range[0]) and is_number(string_range[1]) and len(string_range) == 2:
                plots_start = int(string_range[0])
                plots_end = int(string_range[1])+1
                if int(plots_start) < int(plots_end):
                    sequence = range(plots_start, plots_end)
                    plots.extend(sequence)
                else:
                    sys.exit(errormsg_range_error)
            else:
                sys.exit(errormsg_not_recognised)
        else:
            sys.exit(errormsg_not_recognised)
        
    return sorted(set(plots)) # remove duplicates and sort