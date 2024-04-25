FROM python:3.12-slim as builder

WORKDIR /tmp

# Install Poetry
RUN pip install poetry

# Copy only requirements to cache them in docker layer
COPY ./pyproject.toml ./poetry.lock* /tmp/

# Project initialization:
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.12-slim as runtime

# Working directory
WORKDIR /srv

# Install dependencies
COPY --from=builder /tmp/requirements.txt .
RUN pip install --no-cache-dir --upgrade -r /srv/requirements.txt

# Copy the application files
COPY ./fastpng /srv/app

# Expose port for the application
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]