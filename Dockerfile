FROM continuumio/miniconda3:4.10.3

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
RUN echo "conda activate wenet_fastapi" >> ~/.bashrc
SHELL ["conda", "run", "-n", "wenet_fastapi", "/bin/bash", "-c"]
EXPOSE 8000
CMD ["python", "-m", "personal_context_builder.wenet_cli_entrypoint", "--app_run"]