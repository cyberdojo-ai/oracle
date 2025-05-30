## ------------------------------- Builder Stage ------------------------------ ## 
FROM python:3.11-bookworm AS builder


RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential && \
    mkdir -p /opt/bob/.venv

WORKDIR /opt/bob

COPY ./pyproject.toml .

# Initiate the virtual environment and install the dependencies
ADD pyproject.toml /opt/bob/
ADD poetry.lock /opt/bob/
RUN python -m venv /opt/bob/.venv \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir poetry \
    && poetry --no-cache install --only main


## ------------------------------- Production Stage ------------------------------ ##
FROM python:3.11-slim-bookworm AS production

SHELL [ "/bin/bash", "-c" ]

ARG BUILD_DEPS="build-essential curl ca-certificates unzip"

# Install psql client v16
RUN apt-get update && apt-get install --no-install-recommends -y ${BUILD_DEPS} && \
    install -d /usr/share/postgresql-common/pgdg && \
    curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc && \
    echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    apt-get update  && \
    apt-get install -y postgresql-client-16 && \
    apt-get purge --auto-remove -y ${BUILD_DEPS} && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN /usr/sbin/addgroup --gid 1000 bob \
    && /usr/sbin/adduser --system --shell /bin/bash --home /home/bob --gid 1000 --uid 1000 bob \
    && /usr/sbin/adduser bob bob\
    && echo 'source /opt/bob/.venv/bin/activate' >> /home/bob/.bashrc

USER bob

WORKDIR /opt/bob

COPY /src src
COPY /api-server.py api-server.py
COPY /enrichment-server.py enrichment-server.py
COPY mcp-server.py mcp-server.py
COPY /alembic alembic
COPY /alembic.ini alembic.ini
COPY /entrypoint.sh entrypoint.sh
COPY --from=builder /opt/bob/.venv .venv

# Set up environment variables for production
ENV PATH="/opt/bob/.venv/bin:$PATH"

# Expose the specified port for FastAPI
EXPOSE $PORT

ENTRYPOINT [ "/opt/bob/entrypoint.sh" ]
