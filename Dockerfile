FROM nikolaik/python-nodejs:python3.9-nodejs18-slim AS compile-image

MAINTAINER Hamza Adami <me@adamihamza.com>
ENV GATSBY_TELEMETRY_DISABLED=1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
WORKDIR /opt/app

# Install build deps, then run `pip install`, then remove unneeded build deps all in a single step.
RUN apt-get update \
    && apt-get install --no-install-recommends -y build-essential git \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m venv $VIRTUAL_ENV \
    && python3 -m pip install --upgrade pip

# Install Backend Dependencies
COPY app/leek/requirements.txt /opt/app/leek/
RUN pip3 install -r /opt/app/leek/requirements.txt

# Install additional dependencies for release script
RUN pip3 install requests

# Install Frontend Dependencies
COPY app/web/package.json app/web/yarn.lock /opt/app/web/
RUN yarn --ignore-optional --cwd /opt/app/web

# Add application to container
ADD app/web ./web

# Build Frontend Application, and clean Frontend dependencies and code, Keeping only the dist
RUN yarn --cwd /opt/app/web build \
    && mv /opt/app/web/public /opt/app/public \
    && rm -rf /opt/app/web

ADD app/bin /opt/app/bin
ADD app/conf /opt/app/conf
ADD app/leek /opt/app/leek
COPY release_with_sync.py /opt/app/

FROM python:3.9-slim-buster AS runtime-image

WORKDIR /opt/app
ENV DEBIAN_FRONTEND=noninteractive
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV LEEK_ENV=PROD
ENV PYTHONUNBUFFERED=1

# Heroku-specific environment variables
ENV LEEK_ENABLE_API=true
ENV LEEK_ENABLE_AGENT=true  
ENV LEEK_ENABLE_WEB=true

# Use local Elasticsearch instead of external services
ENV LEEK_ES_URL=http://localhost:9200

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    wget \
    nginx \
    supervisor \
    procps \
    netcat-traditional \
    curl \
    openjdk-11-jre-headless \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /etc/ssl/certs/java \
    && /var/lib/dpkg/info/ca-certificates-java.postinst configure || true

# Install Heroku CLI for release script
RUN curl https://cli-assets.heroku.com/install.sh | sh

# Download and install Elasticsearch directly (avoid package manager issues)
RUN wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.10.1-linux-x86_64.tar.gz \
    && tar -xzf elasticsearch-7.10.1-linux-x86_64.tar.gz \
    && mv elasticsearch-7.10.1 /opt/elasticsearch \
    && rm elasticsearch-7.10.1-linux-x86_64.tar.gz

# Create elasticsearch directories with proper permissions
RUN mkdir -p /opt/elasticsearch/data /opt/elasticsearch/logs /opt/elasticsearch/config \
    && chmod -R 755 /opt/elasticsearch

COPY --from=compile-image /opt /opt

# Copy Elasticsearch configuration
COPY app/conf/elasticsearch-heroku.yml /opt/elasticsearch/config/elasticsearch.yml
RUN chmod 644 /opt/elasticsearch/config/elasticsearch.yml

ARG LEEK_VERSION="-.-.-"
ARG LEEK_RELEASE_DATE="0000/00/00 00:00:00"
ENV LEEK_VERSION=$LEEK_VERSION
ENV LEEK_RELEASE_DATE=$LEEK_RELEASE_DATE

# Create nginx run directory  
RUN mkdir -p /var/run/nginx

# Force cache invalidation for nginx fix
RUN echo "nginx-fix-$(date +%s)" > /tmp/cache-bust

# Expose port (Heroku will assign the PORT environment variable)
EXPOSE $PORT

CMD ["/usr/bin/supervisord", "-c", "/opt/app/conf/supervisord-heroku.conf"] 