#! /bin/bash
PCB_IS_UNITTESTING=1 coverage run --source=personal_context_builder -m unittest discover -s personal_context_builder && coverage report