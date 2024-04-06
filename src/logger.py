import logging
import os

log = logging.getLogger("main")


class Logger:

    @staticmethod
    def log(messages: str | list = "", options: dict = None) -> None:
        level_num = logging.DEBUG if options['level'] is "debug" else logging.INFO
        exc_info = options['exc_info']
        show_hints = os.environ.get('SHOW_HINTS', "true") == "true"

        if options['hint'] is True and show_hints is False:
            return

        if options['white_lines'] and options['white_lines'].__contains__("b"):
            log.log(level_num, "")

        if messages.__class__ == str:
            messages = messages.split("\n")
        for message in messages:
            log.log(level_num, message, exc_info=exc_info)

        if options['white_lines'] and options['white_lines'].__contains__("t"):
            log.log(level_num, "")

    @staticmethod
    def debug(messages: str | list = "", options: dict = None) -> None:
        options['level'] = "debug"
        Logger.log(messages, options)
