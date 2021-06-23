#!/bin/bash
echo `ss -lupn src :5002 | grep 5002 | awk -F " " '{printf $6 "\n"}' | sed 's/.\+pid=\([0-9]\+\).\+/\1/g'` | xargs kill
echo "Kill listeners done"
