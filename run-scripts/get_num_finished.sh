#!/usr/bin/bash
# Get the number of completed MESA runs
find . -name "mesa_finished_*.txt" | wc -l
