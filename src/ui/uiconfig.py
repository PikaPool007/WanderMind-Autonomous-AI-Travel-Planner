import logging
from configparser import ConfigParser
from src.tools.logger import logger  # Shared logger import


class Config:
    def __init__(self, config_file='.\\src\\ui\\uiconfig.ini'):
        self.config = ConfigParser()
        self.config.read(config_file)
        logger.info("Config initialized with file: %s", config_file)

    def get_page_title(self):
        title = self.config["DEFAULT"].get("PAGE_TITLE")
        logger.info("Fetched PAGE_TITLE: %s", title)
        return title