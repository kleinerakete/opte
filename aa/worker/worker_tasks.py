import logging
import time
import signal
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def signal_handler(sig, frame):
    logger.info('Worker shutting down gracefully...')
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("PUZSCAN Worker started")
    logger.info("Worker is ready to process jobs")
    
    try:
        while True:
            logger.debug("Worker checking for jobs...")
            time.sleep(30)
    except KeyboardInterrupt:
        logger.info("Worker interrupted")
        sys.exit(0)