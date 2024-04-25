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
WORKDIR /app

# Install dependencies
COPY --from=builder /tmp/requirements.txt .
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy the application files
COPY ./fast-png /app

# Expose port for the application
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]