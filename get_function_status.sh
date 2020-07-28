#!/bin/bash
if pgrep -x "$1" > /dev/null
then
    echo "Running"
else
    echo "Stopped"
fi