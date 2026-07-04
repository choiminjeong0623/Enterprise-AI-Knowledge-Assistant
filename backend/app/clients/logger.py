import logging

logger = logging.getLogger("enterprise-ai")
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s %(name)s - %(message)s"
)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)