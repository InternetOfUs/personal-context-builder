FROM ubuntu:18.04

ENV TZ=Europe/Zurich

WORKDIR /personal_context_builder
RUN apt-get -y update && apt-get install -y \
    git \
    python3-pip \
    && rm -rf /var/lib/apt/lists/* \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

COPY *.deb .
RUN dpkg -i *.deb && apt-get install -f

COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python3", "-m", "personal_context_builder.wenet_cli_entrypoint", "--app_run"]