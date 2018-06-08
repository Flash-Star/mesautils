#!/usr/bin/bash
# Copy in the MESA executable and make directory compiled for Seawulf
list_file_tasks copy_executable.template -re '\Ac[0-9]+\Z' -o copy_executable.tasks
mpirun -n 1 mpiproc_exec -nchk 0 copy_executable.tasks > copy_executable.log
