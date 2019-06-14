FROM ubuntu:18.04

ENV TZ=Europe/Zurich

WORKDIR /personal_context_builder
RUN apt-get -y update && apt-get install -y \
    python3-pip \
    && rm -rf /var/lib/apt/lists/* \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python3", "-m", "wenet_cli_entrypoint", "--app_run"]