FROM python:alpine

WORKDIR /nyaa-watcher

COPY requirements.txt ./

COPY src/__init__.py config.py logger.py watcher.py webhook.py ./

COPY src/json/config.json history.json watchlist.json webhooks.json /watcher/

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./__init__.py" ]