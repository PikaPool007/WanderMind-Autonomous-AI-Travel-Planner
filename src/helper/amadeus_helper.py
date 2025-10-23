import os
from dotenv import load_dotenv
from amadeus import Client, ResponseError

from src.tools.logger import logger

load_dotenv()
os.environ["AMADEUS_CLIENT_ID"] = os.getenv("AMADEUS_CLIENT_ID")
os.environ["AMADEUS_CLIENT_SECRET"] = os.getenv("AMADEUS_CLIENT_SECRET")


class AmadeusHelper:
    def __init__(self):
        logger.info("AmadeusHelper initialized")

    @staticmethod
    def create_client(hostname="test"):
        logger.info(f"Initializing Amadeus client with hostname: {hostname}")
        try:
            client = Client(
                client_id=os.getenv("AMADEUS_CLIENT_ID"),
                client_secret=os.getenv("AMADEUS_CLIENT_SECRET"),
                hostname=hostname
            )
            logger.info("✅ Amadeus client initialized successfully")
            return client

        except Exception as e:
            logger.error("❌ Failed to initialize Amadeus client", exc_info=True)
            raise
