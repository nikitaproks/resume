# Use an official Python runtime as the base image
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_VERSION=1.6.1
ENV POETRY_VENV=/opt/poetry-venv

# Install poetry separated from system interpreter
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Add `poetry` to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

# Set the working directory in the container
WORKDIR /app

# Copy the project files into the container
COPY . /app
RUN chmod +x /app/manage.py

# Export the dependencies to a requirements.txt file
RUN poetry install --no-interaction --no-ansi

RUN  poetry run python manage.py collectstatic --noinput

#TODO: Is this safe in production?
RUN adduser --disabled-password --gecos '' myuser
USER myuser