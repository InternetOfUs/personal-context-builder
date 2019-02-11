#!/usr/bin/env bash

echo "Running pre-commit hook"
echo "Running tests script 'run_tests.sh'"
./run_tests.sh > /dev/null 2>&1

# $? stores exit value of the last command
if [ $? -ne 0 ]; then
 echo -e "[ \e[91mfailed\e[0m ] Tests, please run 'run_tests.sh' to see what's wrong"
 exit 1
fi

echo -e "[ \e[92mOK\e[0m ] Tests"

