FROM ubuntu:18.04

WORKDIR /personal_context_builder
RUN apt-get -y update && apt-get -y upgrade && apt-get install -y python3-pip
ADD requirements.txt .
RUN pip3 install -r requirements.txt
ADD . .
EXPOSE 8000
CMD ["python3", "-m", "wenet_cli_entrypoint", "--app_run"]