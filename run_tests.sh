#! /bin/bash
if [ "$HOSTNAME" != "redbull" ]
then
    coverage run --source=personal_context_builder -m unittest discover -s personal_context_builder && coverage report
else
    echo "Warning - Test skipped on this computer"
fi
