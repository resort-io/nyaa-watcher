FROM python:alpine

WORKDIR /nyaa-watcher

COPY requirements.txt src/__init__.py src/config.py src/functions.py src/logger.py src/updates.py src/watcher.py src/webhooker.py ./

COPY src/json/config.json src/json/history.json src/json/subscriptions.json src/json/webhooks.json /watcher/

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./__init__.py" ]