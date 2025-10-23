import streamlit as st
import os
import logging

from src.ui.uiconfig import Config
from src.tools.logger import logger

class LoadStreamlitUI:
    def __init__(self):
        self.config = Config()
        self.user_controls = {}
        logger.info("Initialized LoadStreamlitUI class.")

    def load_streamlit_ui(self):
        logger.info("Loading Streamlit UI started.")
        st.set_page_config(page_title=self.config.get_page_title(), layout="wide")
        st.header(self.config.get_page_title())
        logger.info("Streamlit UI loaded successfully with title: %s", self.config.get_page_title())
        return self.user_controls
