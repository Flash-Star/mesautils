#!/usr/bin/bash
if [[ -e grid_status.txt ]]; then rm grid_status.txt; fi
list_file_tasks assess_status.template -re '\Ac[0-9]+\Z' -o assess_status.tasks
bash assess_status.tasks
nr=$(cat grid_status.txt | wc -l)
ns=$(grep "success" grid_status.txt | wc -l)
ne=$(grep "error" grid_status.txt | wc -l)
nt=$(grep "terminated" grid_status.txt | wc -l)
echo "----------------------------------------" >> grid_status.txt
echo "$nr total runs" >> grid_status.txt
echo "$ns runs completed successfully" >> grid_status.txt
echo "$ne runs failed with an error code" >> grid_status.txt
echo "$nt runs failed with no error code" >> grid_status.txt
