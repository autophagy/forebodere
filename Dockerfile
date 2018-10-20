FROM python:3.6-slim

RUN mkdir -pv /app
ADD forebodere /app/forebodere
ADD requirements.txt /app/requirements.txt

WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "-m", "forebodere", "--hord", "forebodere.hord", "-v"]
