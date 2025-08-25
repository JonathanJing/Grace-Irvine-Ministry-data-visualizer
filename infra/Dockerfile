FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

# Ensure configs directory exists and has proper permissions
RUN mkdir -p /app/configs

# Streamlit config
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_HEADLESS=true
ENV PORT=8080
ENV PYTHONPATH=/app

EXPOSE 8080

CMD ["streamlit", "run", "app/ui.py", "--server.port=8080", "--server.address=0.0.0.0"]


