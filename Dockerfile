# FROM python:3.11-slim

# # Prevent Python from writing .pyc files
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# # System dependencies (IMPORTANT for lxml, psycopg2, faiss)
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     gcc \
#     g++ \
#     libpq-dev \
#     libxml2-dev \
#     libxslt1-dev \
#     curl \
#     # ---- Playwright / Chromium deps ----
#     wget \
#     ca-certificates \
#     fonts-liberation \
#     libnss3 \
#     libatk-bridge2.0-0 \
#     libatk1.0-0 \
#     libcups2 \
#     libxkbcommon0 \
#     libxcomposite1 \
#     libxdamage1 \
#     libxfixes3 \
#     libxrandr2 \
#     libgbm1 \
#     libdrm2 \
#     libasound2 \
#     libglib2.0-0 \
#     && rm -rf /var/lib/apt/lists/*

# # Set working directory
# WORKDIR /app

# # Install Python dependencies first (better Docker caching)
# COPY requirements.txt .

# RUN pip install --upgrade pip \
#     && pip install --no-cache-dir -r requirements.txt \
#     && pip install playwright \
#     && playwright install chromium

# # Copy project
# COPY . .

# ENV PYTHONPATH=/app/app

# # Expose FastAPI port
# EXPOSE 8000

# # Run FastAPI
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# -----------------------------
# System dependencies
# -----------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    curl \
    wget \
    ca-certificates \
    fonts-liberation \
    \
    # ---- Playwright / Chromium deps ----
    libnss3 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libdrm2 \
    libasound2 \
    libglib2.0-0 \
    libpango-1.0-0 \
    libcairo2 \
    \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# -----------------------------
# Python dependencies
# -----------------------------
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir playwright \
    && playwright install chromium

# -----------------------------
# App code
# -----------------------------
COPY . .

ENV PYTHONPATH=/app/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]