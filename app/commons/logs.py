import logging
import os
import sys

format_ = "%(asctime)s | %(levelname)-7s | %(module)s.%(funcName)s:%(lineno)d | %(message)s"


def get_lambda_logger() -> logging.Logger:
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(logging.Formatter(format_))
    logger_ = logging.getLogger(os.environ.get("AWS_LAMBDA_FUNCTION_NAME", "NoLambdaEnvironment"))
    logger_.propagate = False
    logger_.setLevel(logging.INFO)
    stdout_handler.setLevel(logging.INFO)
    logger_.addHandler(stdout_handler)
    return logger_


logger = get_lambda_logger()
