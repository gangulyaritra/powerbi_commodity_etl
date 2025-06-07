FROM ghcr.io/astral-sh/uv:debian

LABEL maintainer="aritraganguly.in@protonmail.com"

RUN apt update && apt upgrade -y

# Set the Chrome repository.
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list

# Install Dependencies.
RUN apt-get update \
    && apt-get -y install google-chrome-stable xvfb awscli \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# Environment variables.
ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

ENTRYPOINT ["/bin/bash"]
