import logging
import os

log = logging.getLogger("main")


class Logger:

    @staticmethod
    def log(messages: str | list = "", options: dict = None) -> None:
        """
        Logs messages with the specified options.

        Args:
            messages (Union[str, list], optional): The messages to be logged. Can be a string or a list of strings. Defaults to "".
            options (Optional[dict], optional): A dictionary containing options for logging.
                The `level` key can be used to specify the logging level ("debug" or "info").
                The `exc_info` key can be used to determine whether exception information should be logged.
                The `tip` key can be used to specify whether the message is a tip.
                The `white_lines` key can be used to specify whether white lines should be logged before and/or after the message.
                Defaults to None.

        Returns:
            None
        """
        level_num: int = logging.DEBUG if options and options.get('level') == "debug" else logging.INFO
        exc_info: bool = options.get('exc_info') if options and options.get('exc_info') else False
        log_tips = os.environ.get('LOG_TIPS', "true").lower() == "true"

        if options and options.get('tip') is True and log_tips is False:
            return

        if options and options.get('white_lines') and "t" in options.get('white_lines'):
            log.log(level_num, "")

        if messages.__class__ == str:
            messages = messages.split("\n")
        for message in messages:
            if options and options.get('tip') is True:
                message = f"[Tip] {message}"
            elif level_num == logging.DEBUG and message != "":
                message = f"[DEBUG] {message}"
            log.log(level_num, message, exc_info=exc_info)

        if options and options.get('white_lines') and "b" in options.get('white_lines'):
            log.log(level_num, "")

    @staticmethod
    def debug(messages: str | list = "", options: dict = None) -> None:
        """
        Logs debug messages with the specified options.

        Args:
            messages (Union[str, list], optional): The messages to be logged. Can be a string or a list of strings. Defaults to "".
            options (Optional[dict], optional): A dictionary containing options for logging.
                The `level` key can be used to specify the logging level ("debug" or "info").
                The `exc_info` key can be used to determine whether exception information should be logged.
                The `tip` key can be used to specify whether the message is a tip.
                The `white_lines` key can be used to specify whether white lines should be logged before and/or after the message.
                Defaults to None.

        Returns:
            None
        """
        if options:
            options['level'] = "debug"
        else:
            options = {'level': "debug"}
        Logger.log(messages, options)
