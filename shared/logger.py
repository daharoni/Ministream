import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name, log_file, level=logging.INFO, max_size=5*1024*1024, backup_count=3):
    """Function to setup as many loggers as you want"""

    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    handler = RotatingFileHandler(log_file, maxBytes=max_size, backupCount=backup_count)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# Create loggers for different components
edge_node_logger = setup_logger('edge_node', 'logs/edge_node.log')
network_api_logger = setup_logger('network_api', 'logs/network_api.log')
gui_logger = setup_logger('gui', 'logs/gui.log')
