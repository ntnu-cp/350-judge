FROM python:3.8-slim

WORKDIR /noj-350
RUN apt update && apt install -y gcc
# Get poetry
RUN pip install poetry
# Install
COPY pyproject.toml .
COPY poetry.lock .
RUN poetry install --no-dev
COPY judge.py .

ENTRYPOINT ["poetry", "run", "python", "judge.py"]

CMD [ "--help" ]
