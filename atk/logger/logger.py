import logging.config
import os

os.makedirs("logs", exist_ok=True)

import yaml

config_path = os.path.join(os.path.dirname(__file__), "config.yml")

with open(config_path, "r") as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)

logging.config.dictConfig(config)
