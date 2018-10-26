FROM python:3.6-slim as python-base

RUN apt-get update && apt-get install -y git
COPY requirements.txt .
RUN pip install --ignore-installed --no-user --prefix /install -r requirements.txt

FROM python:3.6-alpine

RUN mkdir -pv /app
WORKDIR /app

COPY setup.py .
COPY forebodere.hord .
COPY forebodere ./forebodere

COPY --from=python-base /install /usr/local

RUN pip install -e .

ENTRYPOINT ["forebodere", "--hord", "forebodere.hord", "-v"]
