FROM python:3.11.9-slim

RUN pip install --no-cache-dir pipx && \
    pipx ensurepath

ENV POETRY_VERSION=2.0.1
RUN pipx install poetry==$POETRY_VERSION
ENV PATH="/root/.local/bin:$PATH"

# For debug
RUN poetry --version

WORKDIR /app

COPY pyproject.toml poetry.lock* README.md ./

# Install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

COPY . .

EXPOSE 8010
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8010"]
