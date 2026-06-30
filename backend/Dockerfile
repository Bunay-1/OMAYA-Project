# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies only once
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Final Image
FROM python:3.11-slim

WORKDIR /app

# Create a non-root user
RUN groupadd -r omaya && useradd -r -g omaya omaya

# Copy only the installed packages from builder
COPY --from=builder /root/.local /home/omaya/.local
COPY . .

# Ensure permissions
RUN chown -R omaya:omaya /app && \
    mkdir -p /app/models && \
    chown -R omaya:omaya /app/models

# Ensure scripts in .local/bin are in PATH
ENV PATH=/home/omaya/.local/bin:$PATH

RUN apt-get update && apt-get install -y curl libpq5 && rm -rf /var/lib/apt/lists/*

USER omaya

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
