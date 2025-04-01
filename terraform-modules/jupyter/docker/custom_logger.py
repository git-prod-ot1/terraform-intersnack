import logging
import os
import sys


class StreamToLogger(object):

    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())

    def flush(self):
        pass


def get_logger(name: str):
    logging.basicConfig()

    logger = logging.getLogger(f"{os.environ.get('FACTORY') or 'none'}_{name}")
    logger.setLevel(logging.INFO)
    sys.stdout = StreamToLogger(logger, logging.INFO)
    sys.stderr = StreamToLogger(logger, logging.ERROR)
    return logger
