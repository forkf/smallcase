import logging

def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s - %(name)s - %(filename)s:%(lineno)s - %(funcName)s()] - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    return logger

LOGGER = get_logger("Smallcase")

HEADERS = ['Symbol', 'Quantity', 'Average Price', 'Current Price', 'P/L']