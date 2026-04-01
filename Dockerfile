FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8502

HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8502/_stcore/health')" || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", \
    "--server.port=8502", \
    "--server.address=0.0.0.0", \
    "--server.headless=true", \
    "--browser.gatherUsageStats=false", \
    "--server.enableCORS=false", \
    "--server.enableXsrfProtection=false", \
    "--server.baseUrlPath=quantmini"]
