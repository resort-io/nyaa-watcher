import logging
import os

log = logging.getLogger("main")


class Logger:

    @staticmethod
    def log(messages: str | list = "", options: dict = None) -> None:
        level_num: int = logging.DEBUG if options and options.get('level') == "debug" else logging.INFO
        exc_info: bool = options.get('exc_info') if options and options.get('exc_info') else False
        show_hints = os.environ.get('SHOW_HINTS', "true").lower() == "true"

        if options and options.get('hint') is True and show_hints is False:
            return

        if options and options.get('white_lines') and options.get('white_lines').__contains__("t"):
            log.log(level_num, "")

        if messages.__class__ == str:
            messages = messages.split("\n")
        for message in messages:
            if level_num == logging.DEBUG:
                message = f"[DEBUG] {message}"
            log.log(level_num, message, exc_info=exc_info)

        if options and options.get('white_lines') and options.get('white_lines').__contains__("b"):
            log.log(level_num, "")

    @staticmethod
    def debug(messages: str | list = "", options: dict = None) -> None:
        if options:
            options['level'] = "debug"
        else:
            options = {'level': "debug"}
        Logger.log(messages, options)
