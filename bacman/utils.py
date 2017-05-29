import logging
logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)


def is_positive_number(value):
    try:
        value = int(value)
        return value > 0
    except ValueError as e:
        logger.exception(e)
