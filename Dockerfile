FROM python:alpine

WORKDIR /nyaa-watcher

COPY src/main.py config.py watcher.py webhook.py requirements.txt ./

COPY src/config.json history.json watchlist.json webhooks.json /watcher/

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./main.py" ]