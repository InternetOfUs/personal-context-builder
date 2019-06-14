#! /bin/bash
if [ "$HOSTNAME" != "redbull" ]
then
    coverage run --source=wenet_pcb -m unittest discover -s wenet_pcb && coverage report
else
    echo "Warning - Test skipped on this computer"
fi
