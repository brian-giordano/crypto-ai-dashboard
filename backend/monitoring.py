import os
import psutil
import logging

def log_memory_usage(context: str = ""):
    """
    Logs the current memory usage of the process.
    :param context: A string to provide context for the log (e.g., "After processing message").
    """
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    logging.info(f"{context} - Memory usage: {memory_info.rss / 1024 ** 2:.2f} MB")