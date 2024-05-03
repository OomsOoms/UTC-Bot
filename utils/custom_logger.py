import logging

class LoggingFormatter(logging.Formatter):
    # Colors and styles
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        format_str = (
            f"{self.black}{self.bold}{{asctime}}{self.reset} "
            f"{log_color}{{levelname:<8}}{self.reset} "
            f"{self.green}{{name}}{self.reset} "
            f"{self.bold}{{message}}{self.reset}"
        )
        formatter = logging.Formatter(format_str, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)

class CustomLogger:
    
    def __new__(cls, name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(LoggingFormatter())

        # File handler
        file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="a+")
        file_handler_formatter = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{")
        file_handler.setFormatter(file_handler_formatter)

        # Add the handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger

"""
# Create a logger object
logger = CustomLogger(__name__)

# Usage examples
logger.info("This is an information message.")
logger.debug("This is a debug message.")
logger.warning("This is a warning message.")
logger.error("This is an error message.")
logger.critical("This is a critical message.")
"""
