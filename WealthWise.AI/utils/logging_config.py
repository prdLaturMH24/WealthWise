"""
Logging configuration for FinGPT Financial AI Services
"""

import logging
import sys
from datetime import datetime

def setup_logging():
    """Setup basic logging configuration"""

    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(stack_info)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('fingpt_app.log')
        ]
    )

    # Reduce noise from external libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)

    logging.info("Logging configuration completed")

class RequestLogger:
    """Simple request logging middleware"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Log request
        logger = logging.getLogger("request")
        logger.info(f"Request: {scope['method']} {scope['path']}")

        await self.app(scope, receive, send)
