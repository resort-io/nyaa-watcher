import logging
import os

log = logging.getLogger("main")


class Logger:

    @staticmethod
    def log(messages: str | list = "", options: dict = None) -> None:
        level_num: int = logging.DEBUG if options and options.get('level') == "debug" else logging.INFO
        exc_info: bool = options.get('exc_info') if options and options.get('exc_info') else False
        show_tips = os.environ.get('SHOW_TIPS', "true").lower() == "true"

        if options and options.get('tip') is True and show_tips is False:
            return

        if options and options.get('white_lines') and "t" in options.get('white_lines'):
            log.log(level_num, "")

        if messages.__class__ == str:
            messages = messages.split("\n")
        for message in messages:
            if options and options.get('tip') is True:
                message = f"[Tip] {message}"
            if level_num == logging.DEBUG:
                message = f"[DEBUG] {message}"
            log.log(level_num, message, exc_info=exc_info)

        if options and options.get('white_lines') and "b" in options.get('white_lines'):
            log.log(level_num, "")

    @staticmethod
    def debug(messages: str | list = "", options: dict = None) -> None:
        if options:
            options['level'] = "debug"
        else:
            options = {'level': "debug"}
        Logger.log(messages, options)
