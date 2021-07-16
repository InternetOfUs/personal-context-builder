FROM continuumio/miniconda3:4.9.2

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

COPY environment.yml environment.yml
RUN conda env create -f environment.yml
COPY . .
EXPOSE 8000
CMD ["conda", "run", "-n", "wenet_fastapi", "python", "-m", "personal_context_builder.wenet_cli_entrypoint", "--app_run"]