FROM ubuntu:18.04

WORKDIR /personal_context_builder
ADD . .
RUN ls
RUN apt-get -y update && apt-get -y upgrade && apt-get install -y python3-pip
RUN pip3 install -r requirements.txt
RUN coverage run --source=. -m unittest discover