#!/usr/bin/bash
if [[ -e grid_status_all.txt ]]; then rm grid_status_all.txt; fi
list_file_tasks get_grid_status_all.template -re '\Ac[0-9]+\Z' -o get_grid_status_all.tasks
echo "Blocker_scaling_factor  Reimers_scaling_factor  status  index" >> grid_status_all.txt
bash get_grid_status_all.tasks
sort_by_index.py grid_status_all.txt -o grid_status_all_sorted.txt
