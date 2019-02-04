#!/usr/bin/env bash

echo "Running pre-commit hook"
echo "Running tests script 'run_tests.sh'"
./run_tests.sh > /dev/null 2>&1

# $? stores exit value of the last command
if [ $? -ne 0 ]; then
 echo -e "\e[91mtests failed\e[0m, please run 'run_tests.sh' to see what's wrong"
 exit 1
fi

echo -e "\e[92mtests succeed\e[0m"

