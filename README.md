# Plotpot

Plotpot is a Python module that plots potentiostatic data automatically imported with [Convpot](https://github.com/ahpohl/convpot). It keeps a journal with meta information such as mass of active material, capacity etc. for later use.

## Getting Started

### Prerequisites

Plotpot is based on the following software and Python packages:

* [Convpot](https://github.com/ahpohl/convpot)
* [Python](https://www.python.org/)
* [NumPy](http://www.numpy.org/)
* [SciPy](https://scipy.org/)
* [Matplotlib](https://matplotlib.org/)

To get the Python environment running under Windows I recommend to use a scientific Python distribution such as [Anaconda](https://www.continuum.io/downloads) or [Enthought Canopy](https://www.enthought.com/products/canopy/), which include precompiled versions of NumPy, SciPy and Matplotlib.

### Installing

To install Plotpot follow these steps (tested under Windows 7 64 bit as a normal user):

* Download and install the [latest Convpot](https://github.com/ahpohl/convpot/releases/latest) package. During installation choose to add Convpot to the PATH of the current user.
* Download and install [Anaconda](https://www.continuum.io/downloads). Choose the Python 3 64 bit version and install "Just for me".
* Create a new virtual Python environment just for running Plotpot. Open an "Anaconda Prompt" and type:
```
blah
```

## Usage

Plotpot.py has the ability to export the raw data in [csv format](https://en.wikipedia.org/wiki/Comma-separated_values) for further processing with e.g. [Microcal Origin](http://www.originlab.com/) or similar software.

### Single file



### Command-line Options

* **--help or -h** - show convpot help
* **--version or -V** - show the version header
* **--verbose or -v** - print verbose output, can be given multiple times to increase verbosity
* **--info or -i** - display supported instruments
* **--timer** - benchmark the program run time, useful for very large files
* **--output FILE** - give alternative output filename. The default is the name of the first input file
* **--merge FILE** - a file with filenames to merge one by line. A "!" denotes a comment.
* **--smooth LEVEL** - smooth current and voltage data (level 1-4). Useful for dQ/dV plots which show artefacts due to noise.

## Authors

* **Alexander Pohl** - *Initial work*

See also the list of [CONTRIBUTORS](https://github.com/ahpohl/convpot/blob/master/CONTRIBUTORS.md) who participated in this project.

## Changelog

All notable changes and releases are documented in the [CHANGELOG](https://github.com/ahpohl/convpot/blob/master/CHANGELOG.md).

## License

This project is licensed under the MIT license - see the [LICENSE](LICENSE) file for details
