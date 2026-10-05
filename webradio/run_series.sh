#!/bin/bash
cd "$(dirname "$0")"
mkdir -p logs
python run_rotation.py > logs/rotation.log 2>&1
echo "ROTATION TERMINEE $(date)" > logs/series_done.log
