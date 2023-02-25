FROM python:3.10-slim
# not using alpine because of numpy

# Ref: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/

ARG REQUIREMENTS_TXT=scraper.requirements.txt

WORKDIR /usr/src/app

# camelot requirements
RUN apt-get update && apt-get install -y \
    ghostscript \
    python3-tk

COPY $REQUIREMENTS_TXT ./
RUN pip install --no-cache-dir -r $REQUIREMENTS_TXT

COPY . .

ENTRYPOINT [ "python", "scraper.py" ]