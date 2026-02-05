
import logging
import sys
from typing import Any

from app.core.config import settings

# Configure logging
def setup_logging():
    """
    Configure the root logger to output to stdout with a standard format.
    In production, this would likely be JSON formatting.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    
    # Quiet down some loud libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    return root_logger

logger = logging.getLogger("app")
