import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

import atk.logger.logger
import logging


logger = logging.getLogger(__name__)

logger.info("info log")
logger.warning("warning log")
logger.error("error log")
logger.critical("critical log")

logger.setLevel(logging.DEBUG)
logger.debug("debug log")
