import os


class Env:
    @staticmethod
    def json_path(filename: str) -> str:
        version = f"/dev.{filename}.json" if os.environ.get("ENV", "production").lower() == "development" else f"/{filename}.json"
        return os.environ.get("WATCHER_DIR", "") + version
