from pydantic import BaseModel, Field
from typing import List
from langchain_core.prompts import ChatPromptTemplate

from src.state.state import TravelPlanState
from src.LLMs.openaillm import OpenAiLLM
from src.tools.tools_for_flights import FlightTools
from src.tools.logger import logger 


class FlightNodes:
    def __init__(self, llm):
        self.llm = llm
        logger.info("FlightNodes initialized with LLM instance")

    # -------------------------------------------------------
    # 1️⃣ Retrieve flight details
    # -------------------------------------------------------
    def get_flight_data(self, state: TravelPlanState) -> dict:
        """
        Fetch flight details using Amadeus API and store them in the state.
        """
        try:
            user_data = state["user_data"]
            origin_city = user_data.get("origin_city")
            destination_city = user_data.get("destination_city")
            departure_date = user_data.get("departure_date")
            return_date = user_data.get("return_date", None)
            adults = user_data.get("num_travelers", 1)

            logger.info(
                f"Fetching flight data | Origin: {origin_city}, "
                f"Destination: {destination_city}, Departure: {departure_date}, Return: {return_date}, Adults: {adults}"
            )

            flight_tool = FlightTools()
            outbound_flights = flight_tool.get_flights(
                origin_city, destination_city, departure_date, adults, top_n=5
            )
            logger.info(f"Retrieved {len(outbound_flights)} outbound flight options")

            return_flights = []
            if return_date:
                return_flights = flight_tool.get_return_flights(
                    origin_city, destination_city, return_date, adults, top_n=5
                )
                logger.info(f"Retrieved {len(return_flights)} return flight options")

            logger.info("Flight data fetched successfully")

            return {
                "flights": {
                    "outbound_flights": outbound_flights,
                    "return_flights": return_flights,
                    "top_flight_summary": ""
                }
            }

        except Exception as e:
            logger.exception(f"Error occurred while fetching flight data: {e}")
            raise

    # -------------------------------------------------------
    # 2️⃣ Summarize top flights with LLM
    # -------------------------------------------------------
    def get_top_flight_summary(self, state: TravelPlanState) -> dict:
        """
        Use Azure LLM to generate summarized flight recommendations.
        """
        try:
            logger.info("Starting top flight summary generation")

            class FlightOption(BaseModel):
                airline: str = Field(..., description="Airline name or carrier code")
                origin: str = Field(..., description="Departure airport code")
                destination: str = Field(..., description="Arrival airport code")
                price: float = Field(..., description="Total price of the flight")
                currency: str = Field(..., description="Currency of the price")
                duration: str = Field(..., description="Flight duration")
                stops: int = Field(..., description="Number of stops")

            class FlightRecommendations(BaseModel):
                recommendations: List[FlightOption]

            llm = self.llm.with_structured_output(FlightRecommendations)
            logger.info("Structured LLM model prepared for flight recommendations")

            user_data = state["user_data"]
            outbound_flights = state["flights"]["outbound_flights"]
            return_flights = state["flights"]["return_flights"]

            system = """
            You are a travel planner AI that helps users choose the best flight options.

            You are provided:
            - Outbound and (if available) return flight data with airline, timing, price, and stops.
            - User trip details and preferences.

            Your task:
            - Recommend top flights based on affordability, duration, and minimal stops.
            - Prefer direct flights if prices are close.
            - Choose only from the given flight data (no hallucination).
            - Output must strictly follow the `FlightRecommendations` schema.

            Outbound Flights:
            {outbound_context}

            Return Flights (if available):
            {return_context}

            User Trip Details:
            {query}
            """

            query = (
                f"Flying from {user_data['origin_city']} to {user_data['destination_city']} "
                f"on {user_data['departure_date']}."
            )
            if user_data.get("return_date"):
                query += f" Returning on {user_data['return_date']}."
            query += (
                f" {user_data['num_travelers']} traveller(s). "
                f"Preferences: {user_data.get('preferences', 'None')}."
            )

            prompt = ChatPromptTemplate.from_template(system)
            chain = prompt | llm

            logger.info(f"Invoking LLM for flight summary | Route: {user_data['origin_city']} → {user_data['destination_city']}")
            top_flight_summary = chain.invoke({
                "outbound_context": outbound_flights,
                "return_context": return_flights,
                "query": query
            })

            logger.info("Successfully generated top flight summary")
            # print(f"Top Flight Summary: {top_flight_summary}")  # ✅ removed in favor of logger

            return {
                "flights": {
                    "outbound_flights": outbound_flights,
                    "return_flights": return_flights,
                    "top_flight_summary": top_flight_summary
                }
            }

        except Exception as e:
            logger.exception(f"Error while generating flight summary: {e}")
            raise