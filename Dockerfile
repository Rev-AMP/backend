FROM ubuntu:focal
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update -y
RUN apt install curl python-is-python3 python3-pip -y
RUN python3 -m pip install poetry
RUN poetry config virtualenvs.create false
COPY app/poetry.lock app/pyproject.toml app/
WORKDIR app
RUN poetry install
ENV PYTHONPATH /app
