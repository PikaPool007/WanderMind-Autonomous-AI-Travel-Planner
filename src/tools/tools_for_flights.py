from amadeus import ResponseError
from src.helper.amadeus_helper import AmadeusHelper
from src.tools.logger import logger


class FlightTools:
    def __init__(self):
        try:
            self.amadeus = AmadeusHelper.create_client(hostname="test")
            logger.info("✈️ Initialized Amadeus client successfully (test environment).")
        except Exception as e:
            logger.exception(f"❌ Failed to initialize Amadeus client: {e}")
            self.amadeus = None

    def get_airport_code(self, city_name: str) -> str:
        """Convert city name to IATA airport code using Amadeus API."""
        if not self.amadeus:
            logger.error("❌ Amadeus client not initialized. Cannot fetch airport code.")
            return None

        try:
            response = self.amadeus.reference_data.locations.get(
                keyword=city_name, subType="AIRPORT"
            )
            if response.data:
                code = response.data[0].get("iataCode")
                if code:
                    logger.info(f"🛫 Found airport code for {city_name}: {code}")
                    return code

            logger.warning(f"⚠️ No airport code found for '{city_name}', using city name fallback.")
            return city_name[:3].upper()

        except ResponseError as e:
            logger.exception(f"❌ Amadeus API error while fetching airport code for '{city_name}': {e}")
            return None
        except Exception as e:
            logger.exception(f"❌ Unexpected error in get_airport_code for '{city_name}': {e}")
            return None

    def get_flights(self, origin_city, destination_city, departure_date, adults=1, top_n=3, currency="USD"):
        """Fetch top N cheapest flights between two cities using Amadeus API."""
        if not self.amadeus:
            logger.error("❌ Amadeus client not initialized. Cannot fetch flights.")
            return []

        origin_code = self.get_airport_code(origin_city)
        destination_code = self.get_airport_code(destination_city)

        if not origin_code or not destination_code:
            logger.error(f"❌ Invalid airport codes: {origin_city}={origin_code}, {destination_city}={destination_code}")
            return []

        try:
            logger.info(f"🔍 Fetching flights from {origin_code} → {destination_code} on {departure_date} for {adults} adult(s).")

            response = self.amadeus.shopping.flight_offers_search.get(
                originLocationCode=origin_code,
                destinationLocationCode=destination_code,
                departureDate=departure_date,
                adults=adults,
                currencyCode=currency,
                max=10
            )

            if not response.data:
                logger.warning(f"⚠️ No flight offers found for route {origin_code} → {destination_code}.")
                return []

            flights = []
            for offer in response.data:
                price = offer.get("price", {}).get("total", 0.0)
                currency_code = offer.get("price", {}).get("currency", currency)
                itineraries = offer.get("itineraries", [])
                if not itineraries:
                    continue

                segments = itineraries[0].get("segments", [])
                if not segments:
                    continue

                departure = segments[0]["departure"]["iataCode"]
                arrival = segments[-1]["arrival"]["iataCode"]
                airline = segments[0]["carrierCode"]
                duration = itineraries[0].get("duration", "N/A")

                flights.append({
                    "airline": airline,
                    "origin": departure,
                    "destination": arrival,
                    "price": float(price),
                    "currency": currency_code,
                    "duration": duration,
                    "stops": len(segments) - 1,
                    "departure_time": segments[0]["departure"]["at"],
                    "arrival_time": segments[-1]["arrival"]["at"]
                })

            sorted_flights = sorted(flights, key=lambda x: x["price"])[:top_n]
            logger.info(f"✅ Retrieved {len(sorted_flights)} flight(s) for route {origin_code} → {destination_code}.")
            return sorted_flights

        except ResponseError as e:
            logger.exception(f"❌ Amadeus API error while fetching flights: {e}")
            return []
        except Exception as e:
            logger.exception(f"❌ Unexpected error while fetching flights: {e}")
            return []

    def get_return_flights(self, origin_city, destination_city, return_date, adults=1, top_n=3, currency="USD"):
        """Fetch return flights (destination → origin)."""
        try:
            logger.info(f"🔄 Fetching return flights for {destination_city} → {origin_city} on {return_date}.")
            return self.get_flights(destination_city, origin_city, return_date, adults, top_n, currency)
        except Exception as e:
            logger.exception(f"❌ Error while fetching return flights: {e}")
            return []
