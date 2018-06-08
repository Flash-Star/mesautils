#!/usr/bin/bash
if [[ -e grid_results.txt ]]; then rm grid_results.txt; fi
if [[ -e grid_results_sorted.txt ]]; then rm grid_results_sorted.txt; fi
list_file_tasks get_grid_results.template -re '\Ac[0-9]+\Z' -o get_grid_results.tasks
echo "Blocker_scaling_factor  Reimers_scaling_factor  star_mass  index" >> grid_results.txt
bash get_grid_results.tasks
sort_by_index.py grid_results.txt -o grid_results_sorted.txt
