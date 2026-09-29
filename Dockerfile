FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv/nexus
COPY pyproject.toml ./
COPY nexus_os ./nexus_os
RUN pip install --no-cache-dir .
RUN useradd -r -u 10001 nexus && mkdir -p /srv/nexus/data && chown -R nexus:nexus /srv/nexus
USER nexus
EXPOSE 8000
CMD ["uvicorn", "nexus_os.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
