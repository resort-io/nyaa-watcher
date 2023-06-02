FROM python:alpine

WORKDIR /nyaa-watcher

COPY main.py config.py watcher.py requirements.txt ./

COPY config.json watchlist.json history.json /watcher/

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./main.py" ]