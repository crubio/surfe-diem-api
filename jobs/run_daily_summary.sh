#!/bin/bash

clear

echo "Running daily summary job...(get_latest_summary.py)"

python3 tools/get_latest_summary.py

echo "Done!"
