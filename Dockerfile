FROM python:3.6-slim

RUN mkdir -pv /app
ADD forebodere.py /app/forebodere.py
ADD requirements.txt /app/requirements.txt

WORKDIR /app
RUN pip install -r requirements.txt
CMD ["sh", "-c", "python forebodere.py --hord forebodere.hord --token $DISCORD_TOKEN -v"]
