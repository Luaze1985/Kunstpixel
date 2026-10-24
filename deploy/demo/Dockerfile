# Datafinner som hostet demo. Bygges fra rotmappen i repoet:
#   docker build -f deploy/demo/Dockerfile -t kunstpixel-datafinner:demo .
#
# Bildet inneholder bare Datafinner-koden og den ferdigbygde museum.db.
# Interne mapper kopieres ikke inn. Caddy krever innlogging frem til oppgave 05.

FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DATAFINNER_HOST=0.0.0.0 \
    DATAFINNER_PORT=8010 \
    KUNSTPIXEL_DB_PATH=/app/data/museum.db

COPY deploy/demo/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Fast bruker uten skall og uten hjemmemappe. Alt under /app er skrivebeskyttet for den.
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin demo
WORKDIR /app
COPY src/__init__.py ./src/__init__.py
COPY src/kunstpixel/__init__.py ./src/kunstpixel/__init__.py
COPY src/kunstpixel/core ./src/kunstpixel/core
COPY src/kunstpixel/adapters/__init__.py src/kunstpixel/adapters/datafinner.py src/kunstpixel/adapters/datafinner_api.py ./src/kunstpixel/adapters/
COPY src/kunstpixel/adapters/datafinner ./src/kunstpixel/adapters/datafinner
COPY 05_data/museum.db ./data/museum.db
RUN chmod -R a-w /app && chmod 444 /app/data/museum.db

USER 10001:10001
EXPOSE 8010
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD ["python", "-c", "import sys, urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8010/api/verktoy?navn=list_roles&args=%7B%7D', timeout=4).status == 200 else 1)"]
CMD ["python", "src/kunstpixel/adapters/datafinner.py"]
