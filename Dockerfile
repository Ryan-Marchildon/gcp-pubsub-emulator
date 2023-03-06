FROM python:3.8-slim-buster

# Install slowly-changing dependencies
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# Install project packages
RUN mkdir -p /src
COPY src/ /src/
RUN pip install -e /src

WORKDIR /src

EXPOSE 8000:8000
