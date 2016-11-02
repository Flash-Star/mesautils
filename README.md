# mesa2flash

Provides a set of classes and mapping routines to port a MESA stellar profile to a uniform grid, e.g. for use with FLASH.

For a use example, see `run.sh`

Also lets you open MESA profile and history files for ease of plotting.

`nuclides.xml` was downloaded from the JINA Reaclib database
[Reaclib homepage](https://groups.nscl.msu.edu/jina/reaclib/db/index.php)

## Dependencies:

Depends on the Nuclides class in nucplotlib, which includes a python interface to the JINA Reaclib nuclide listing.

Download [nucplotlib](https://github.com/dwillcox/nucplotlib) and add it to your PYTHONPATH.

## TODO:

Rewrite with object-orientation for readability.
