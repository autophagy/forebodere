FROM python:3.6-slim

RUN apt-get update && apt-get install -y git

RUN mkdir -pv /app
ADD forebodere /app/forebodere
ADD requirements.txt /app/requirements.txt

WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "-m", "forebodere", "--hord", "forebodere.hord", "-v"]
