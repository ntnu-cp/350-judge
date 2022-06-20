FROM python:3.8-slim

WORKDIR /noj-350
RUN apt update && apt install -y gcc
# Get poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
# Install
RUN poetry install
COPY poetry.lock .
COPY pyproject.toml .
COPY judge.py .

CMD ["poetry", "run", "python", "judge.py"]

