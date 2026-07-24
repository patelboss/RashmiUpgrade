#FROM python:3.10-slim-bookworm
FROM python:3.11.9-slim-bookworm
# 1. Install system dependencies & build tools for TgCrypto
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y git build-essential python3-dev && \
    rm -rf /var/lib/apt/lists/*

# 2. Copy and install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip3 install -U pip urllib3 && \
    pip3 install -U -r /requirements.txt

# 3. Set up working directory and copy application source code
WORKDIR /Rashmibot
COPY . .

# 4. Fix potential Windows script formatting and start
COPY start.sh /start.sh
RUN sed -i 's/\r$//' /start.sh
CMD ["/bin/bash", "/start.sh"]
