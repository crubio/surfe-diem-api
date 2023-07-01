#!/bin/bash

clear

echo "Running summary cleanup job...(delete_old_summaries.py)"

python3 tools/delete_old_summaries.py

echo "Done!"
