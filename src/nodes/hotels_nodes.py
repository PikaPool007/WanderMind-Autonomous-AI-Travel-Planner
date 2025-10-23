from pydantic import BaseModel, Field
from typing import List
from langchain_core.prompts import ChatPromptTemplate

from src.tools.tools_for_hotels import HotelTools
from src.state.state import TravelPlanState
from src.LLMs.openaillm import OpenAiLLM
from src.tools.logger import logger  # ✅ shared logger


class HotelNodes:
    def __init__(self, llm):
        self.llm = llm
        logger.info("HotelNodes initialized with LLM instance")

    def get_hotel_data(self, state: TravelPlanState) -> dict:
        """
        Fetch hotel details using Amadeus API and store in state.
        """
        try:
            user_data = state["user_data"]

            city_name = user_data.get("destination_city")
            check_in = user_data.get("departure_date")
            check_out = user_data.get("return_date")
            adults = user_data.get("num_travelers", 2)
            room_qty = 1

            logger.info(
                f"Fetching hotel data | City: {city_name}, Check-in: {check_in}, "
                f"Check-out: {check_out}, Adults: {adults}, Rooms: {room_qty}"
            )

            hotel_tool = HotelTools()
            hotels = hotel_tool.get_hotels(
                name=city_name,
                check_in=check_in,
                check_out=check_out,
                adults=adults,
                room_quantity=room_qty
            )

            logger.info(f"Retrieved {len(hotels) if hotels else 0} hotels for {city_name}")

            return {
                "hotels": {
                    "all_hotel_data": hotels,
                    "top_hotel_data": ""
                }
            }

        except Exception as e:
            logger.exception(f"Error occurred while fetching hotel data: {e}")
            raise

    def get_top_hotels(self, state: TravelPlanState) -> dict:
        """
        Use Azure LLM to generate summarized top hotel recommendations.
        """
        try:
            logger.info("Starting top hotel recommendations generation")

            class HotelRecommendation(BaseModel):
                name: str = Field(..., description="Hotel name")
                rating: str = Field(..., description="Hotel rating or 'N/A'")
                address: str = Field(..., description="Full address")
                price: float = Field(..., description="Total price")
                currency: str = Field(..., description="Currency code")

            class HotelRecommendations(BaseModel):
                recommendations: List[HotelRecommendation]

            llm = self.llm.with_structured_output(HotelRecommendations)
            logger.info("Structured LLM model prepared for hotel recommendations")

            user_data = state["user_data"]
            hotel_data = state["hotels"]["all_hotel_data"]

            system = """
            You are a travel assistant that summarizes hotel options for a given city.
            You are provided:
            - A list of available hotels with names, ratings, addresses, and prices.
            - The user's travel details (city, duration, preferences).

            Your goal:
            - Recommend the top hotels for the user.
            - Ensure a balance between affordability and quality.
            - Highlight hotels suitable for the user's preferences.
            - Strictly choose from the given hotel list (do not hallucinate).
            - Follow the `HotelRecommendations` schema.

            Hotel Data:
            {context}

            User Trip Details:
            {query}
            """

            query = (
                f"Travelling to {user_data['destination_city']} from {user_data['departure_date']} "
                f"to {user_data['return_date']} with {user_data['num_travelers']} people. "
                f"Preferences: {user_data['preferences']}."
            )

            prompt = ChatPromptTemplate.from_template(system)
            chain = prompt | llm

            logger.info(f"Invoking LLM for top hotels in {user_data['destination_city']}")
            top_hotels = chain.invoke({
                "context": hotel_data,
                "query": query
            })

            logger.info(f"Successfully generated top hotel recommendations for {user_data['destination_city']}")
            # print(top_hotels)  # ✅ removed in favor of logging

            return {
                "hotels": {
                    "all_hotel_data": hotel_data,
                    "top_hotel_data": top_hotels
                }
            }

        except Exception as e:
            logger.exception(f"Error while generating top hotel recommendations: {e}")
            raise
