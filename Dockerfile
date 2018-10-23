FROM python:3.6-slim as python-base

RUN apt-get update && apt-get install -y git
COPY requirements.txt .
RUN pip install --ignore-installed --no-user --prefix /install -r requirements.txt

FROM python:3.6-alpine

RUN mkdir -pv /app
ADD forebodere /app/forebodere
WORKDIR /app

COPY --from=python-base /install /usr/local

ENTRYPOINT ["python", "-m", "forebodere", "--hord", "forebodere.hord", "-v"]
