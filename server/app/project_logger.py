from logging import DEBUG, Formatter, getLogger, Logger, StreamHandler


def get_stream_logger(
    logger_name: str,
) -> Logger:
    logger = getLogger(logger_name)
    stream_handler = StreamHandler()
    stream_handler.setLevel(DEBUG)
    formatter = Formatter(
        "*** %(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s"
    )
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.setLevel(DEBUG)
    return logger


fake_twitter_logger = get_stream_logger("fake_twitter")
