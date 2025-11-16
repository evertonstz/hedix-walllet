# syntax=docker/dockerfile:1

# Use UV's official image with Python 3.11
FROM ghcr.io/astral-sh/uv:python3.11-bookworm AS app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy only what is needed to install the package
COPY pyproject.toml README.md /app/
COPY src /app/src

# Install the package into the system interpreter using UV
RUN uv pip install --system .

# Run the console script defined in pyproject: [project.scripts] wallet = "hedix_wallet.main:main"
CMD ["wallet"]
