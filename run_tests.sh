#! /bin/bash
if [ "$HOSTNAME" != "redbull" ]
then
    coverage run --source=. -m unittest discover && coverage report
else
    echo "Warning - Test skipped on this computer"
fi
