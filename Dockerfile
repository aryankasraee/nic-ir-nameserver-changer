# Multi-stage build for optimized image size
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

# Build arguments for metadata
ARG BUILDTIME
ARG VERSION
ARG REVISION

# Add metadata labels
LABEL org.opencontainers.image.created=$BUILDTIME
LABEL org.opencontainers.image.version=$VERSION
LABEL org.opencontainers.image.revision=$REVISION
LABEL org.opencontainers.image.source="https://github.com/$GITHUB_REPOSITORY"
LABEL org.opencontainers.image.title="NIC.IR Nameserver Changer"
LABEL org.opencontainers.image.description="Automated nameserver changer for NIC.IR domains"
LABEL org.opencontainers.image.vendor="Your Organization"
LABEL org.opencontainers.image.licenses="MIT"

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    xvfb \
    x11vnc \
    fluxbox \
    x11-utils \
    procps \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application files
COPY nameserver_changer.py .
COPY docker_entrypoint.sh .
RUN chmod +x docker_entrypoint.sh

# Create necessary directories
RUN mkdir -p /app/results /app/logs

# Create non-root user for security
RUN groupadd -r nicir && useradd -r -g nicir -d /app -s /sbin/nologin nicir \
    && chown -R nicir:nicir /app

# Set environment variables
ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import selenium; print('OK')" || exit 1

# Switch to non-root user
USER nicir

# Expose VNC port (optional, for debugging)
EXPOSE 5900

# Set entrypoint
ENTRYPOINT ["./docker_entrypoint.sh"]

# Default command
CMD ["python", "nameserver_changer.py"]