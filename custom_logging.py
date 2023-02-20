import google.cloud.logging
import logging

client = google.cloud.logging.Client()

client.setup_logging()

def info(text):
    logging.info(text)