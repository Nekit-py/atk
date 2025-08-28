import logging.config
import os

import yaml

os.makedirs("logs", exist_ok=True)


config_path = os.path.join(os.path.dirname(__file__), "config.yml")

with open(config_path) as stream:
    config = yaml.load(stream, Loader=yaml.SafeLoader)

logging.config.dictConfig(config)
