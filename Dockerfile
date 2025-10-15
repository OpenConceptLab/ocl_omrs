FROM python:3.9-slim-bullseye

# Install OS packages needed to build mysqlclient and other extensions.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      default-mysql-client build-essential libssl-dev libffi-dev libmariadb-dev-compat libmariadb-dev ca-certificates unzip && \
    rm -rf /var/lib/apt/lists/* && \
    python -m pip install --upgrade pip setuptools wheel

COPY ./requirements.txt /app/
COPY ./start.sh /app/

WORKDIR /app

# Install Python requirements (mysqlclient needs build deps installed above)
RUN --mount=type=cache,target=/root/.cache/pip \
  python -m pip install -r requirements.txt

# Use exec form so signals are forwarded to the process inside the container
CMD ["/bin/bash", "./start.sh"]