FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv/nexus
COPY pyproject.toml ./
COPY nexus_os ./nexus_os
RUN pip install --no-cache-dir .
RUN useradd -r -u 10001 nexus && mkdir -p /srv/nexus/data && chown -R nexus:nexus /srv/nexus
USER nexus
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=5 \
  CMD python -c "import json, urllib.request; data=json.load(urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)); raise SystemExit(0 if data.get('status') == 'ok' else 1)"
CMD ["uvicorn", "nexus_os.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
