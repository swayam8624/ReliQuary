"""
Centralized logging configuration for the ReliQuary project.
This module provides a standardized logging setup across all components.
"""

import logging
import logging.config
import os
from typing import Dict, Any

def get_logging_config(log_level: str = "INFO", log_file: str = None) -> Dict[str, Any]:
    """
    Get logging configuration dictionary.
    
    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs to
        
    Returns:
        Dictionary with logging configuration
    """
    # Base configuration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s"
            },
            "json": {
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "standard",
                "stream": "ext://sys.stdout"
            }
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["console"],
                "level": log_level,
                "propagate": False
            },
            "reliquary": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False
            },
            "reliquary.api": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False
            },
            "reliquary.auth": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False
            },
            "reliquary.agents": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False
            },
            "reliquary.zk": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False
            },
            "reliquary.vaults": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False
            }
        }
    }
    
    # Add file handler if log_file is specified
    if log_file:
        # Ensure directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        config["handlers"]["file"] = {
            "class": "logging.FileHandler",
            "level": log_level,
            "formatter": "detailed",
            "filename": log_file,
            "mode": "a"
        }
        
        # Add file handler to all loggers
        for logger_config in config["loggers"].values():
            logger_config["handlers"].append("file")
    
    return config

def setup_logging(log_level: str = "INFO", log_file: str = None) -> logging.Logger:
    """
    Setup centralized logging for the application.
    
    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs to
        
    Returns:
        Root logger instance
    """
    # Get configuration
    config = get_logging_config(log_level, log_file)
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Return root logger
    return logging.getLogger()

# Convenience functions for different log levels
def setup_debug_logging(log_file: str = None) -> logging.Logger:
    """Setup logging with DEBUG level."""
    return setup_logging("DEBUG", log_file)

def setup_info_logging(log_file: str = None) -> logging.Logger:
    """Setup logging with INFO level."""
    return setup_logging("INFO", log_file)

def setup_warning_logging(log_file: str = None) -> logging.Logger:
    """Setup logging with WARNING level."""
    return setup_logging("WARNING", log_file)

def setup_error_logging(log_file: str = None) -> logging.Logger:
    """Setup logging with ERROR level."""
    return setup_logging("ERROR", log_file)