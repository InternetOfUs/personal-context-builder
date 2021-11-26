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
#  To use base instead of wenet_fastapi like in dev
RUN sed -i 's/wenet_fastapi/base/g' environment.yml
RUN conda env update --name base --file environment.yml
COPY . .
EXPOSE 8000
CMD ["python", "-m", "personal_context_builder.wenet_cli_entrypoint", "--app_run"]