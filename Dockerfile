FROM python:alpine

WORKDIR /nyaa-watcher

COPY requirements.txt src/__init__.py src/config.py src/logger.py src/watcher.py src/webhook.py ./

COPY src/json/config.json src/json/history.json src/json/watchlist.json src/json/webhooks.json /watcher/

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./__init__.py" ]