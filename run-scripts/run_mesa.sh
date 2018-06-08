#!/usr/bin/bash
list_file_tasks run_mesa.template -re '\Ac[0-9]+\Z' -o run_mesa.tasks
# Now do 'qsub seawulf.qsub'
