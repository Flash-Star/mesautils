# mesa2flash

Provides a set of classes and mapping routines to port a MESA stellar
profile to a uniform grid, e.g. for use with FLASH.

For a use example, see `run.sh`

Also lets you open MESA profile and history files for ease of plotting.

## Dependencies:

* Either python 2 or 3 (tested to yield the same output with versions
  2.7.10 and 3.5.1)

* numpy

* mpi4py

* periodictable

Also depends on the Nuclides class in nucplotlib, which includes a
python interface to the JINA Nuclear data listing.

Download [nucplotlib](https://github.com/dwillcox/nucplotlib) and add
it to your PYTHONPATH.

