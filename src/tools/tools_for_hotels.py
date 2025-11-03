from amadeus import ResponseError
from serpapi import GoogleSearch

from src.helper.amadeus_helper import AmadeusHelper
from src.tools.logger import logger

import os
import dotenv

dotenv.load_dotenv()
SERP_API_KEY = os.getenv("SERP_API_KEY")

class HotelTools:
    def __init__(self):
        self.amadeus = AmadeusHelper.create_client(hostname="test")
        logger.info("HotelTools initialized with Amadeus test client")

    def fetch_hotels(self, name, check_in, check_out, adults=1, room_quantity=1, currency="USD"):
        """Fetch hotel data using Google Hotels via SerpAPI."""
        logger.info(
            f"Fetching hotels for {name} | check-in: {check_in}, check-out: {check_out}, adults: {adults}"
        )

        params = {
            "engine": "google_hotels",
            "q": name,
            "check_in_date": check_in,
            "check_out_date": check_out,
            "adults": adults,
            "currency": currency,
            "api_key": SERP_API_KEY
        }

        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            properties = results.get("properties", [])
            logger.info(f"✅ Retrieved {len(properties)} hotel results for {name}")
            return properties

        except Exception as e:
            logger.error(f"❌ Error fetching hotels for {name}: {e}", exc_info=True)
            return []
