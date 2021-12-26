FROM python:3.10-slim
RUN pip install poetry
RUN poetry config virtualenvs.create false
COPY app/poetry.lock app/pyproject.toml app/
WORKDIR app
RUN poetry install
ENV PYTHONPATH /app
