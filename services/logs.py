import logging

logging.basicConfig(
    filename="execution.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def log_message(message: str):
    logging.info(message)
