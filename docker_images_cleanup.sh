#!/bin/bash
TOTO=$(docker images | grep "docker.idiap.ch/wenet/personal_context_builder" | grep none | awk '{print $3}')
for value in $TOTO
do
	docker image rm $value
done