import os
from logger import Logger


class Env:
    def __init__(self):
        self.env: str = self.get("ENV", "production").lower()
        Logger.debug(f"Environment: {self.env.upper()}")

    def get(self, key: str, default: str = None) -> str:
        if os.environ.get(key) is not None:
            return os.environ.get(key)
        if os.environ.get(key.lower()) is not None:
            return os.environ.get(key.lower())
        if os.environ.get(key.upper()) is not None:
            return os.environ.get(key.upper())
        if default is not None:
            return default
        raise Exception(f"Environment Error: The '{key}' environment variable does not exist.")

    def path(self, path: str) -> str:
        version = f"/dev.{path}.json" if self.env == "development" else f"/{path}.json"
        return self.get("WATCHER_DIR", "") + version
