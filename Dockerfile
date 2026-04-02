# Use a lightweight Ubuntu base
FROM ubuntu:22.04

# Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install core dependencies
RUN apt-get update && apt-get install -y \
    curl \
    aria2 \
    bc \
    zip \
    nodejs \
    npm \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Rclone
RUN curl https://rclone.org/install.sh | bash

# Install APKMirror Downloader
RUN npm install -g apkmirror-downloader

# Set the working directory
WORKDIR /data

# Default command
CMD ["bash"]
