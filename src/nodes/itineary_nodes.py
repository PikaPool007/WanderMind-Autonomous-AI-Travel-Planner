import logging
from typing import Dict
from langchain_core.messages import AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import json
from datetime import datetime, timedelta

from src.state.state import TravelPlanState
from src.tools.logger import logger

class ItineraryNodes:
    def __init__(self, llm):
        self.llm = llm
        logger.info("Initialized ItineraryNodes with provided LLM instance.")

    def get_itinerary(self, state: TravelPlanState) -> Dict:
        logger.info("Starting itinerary generation process.")

        try:
            prompt = PromptTemplate(
                input_variables=["user_data", "top_flight_data", "top_hotel_data", "top_attr_data"],
                template="""
                    You are a travel planning agent. Using only the provided information, create a **clear and structured** final travel itinerary.

                    User Preferences:
                    {user_data}

                    Top Selected Flights:
                    {top_flight_data}

                    Best Matched Hotels:
                    {top_hotel_data}

                    Major Attractions to Visit:
                    {top_attr_data}

                    Guidelines:
                    - Organize by **Day 1, Day 2, …**
                    - Include flight timings, hotel check-in/out
                    - Include 2-3 attractions per day with travel flow.
                    - Mention what do at the attractions.
                    - Add short tips (travel mode, time to spend).
                    - Format neatly using bullet points + bold headers
                    - Do not mention the total cost or anything like that.
                    - Mention the total travel time at the end of the itinerary.

                    Now create the **final itinerary**.
                """
            )

            logger.info("Prompt template for itinerary successfully created.")

            # Log user data context (truncated to avoid giant logs)
            logger.debug(f"User Data: {json.dumps(state.get('user_data', {}), indent=2)[:500]}")
            logger.debug(f"Top Flight Data: {str(state.get('flights', {}).get('top_flight_summary', ''))[:300]}")
            logger.debug(f"Top Hotel Data: {str(state.get('hotels', {}).get('top_hotel_data', ''))[:300]}")
            logger.debug(f"Top Attraction Data: {str(state.get('attractions', {}).get('top_attr_data', ''))[:300]}")

            response = self.llm.invoke(
                prompt.format(
                    user_data=state["user_data"],
                    top_flight_data=state["flights"]["top_flight_summary"],
                    top_hotel_data=state["hotels"]["top_hotel_data"],
                    top_attr_data=state["attractions"]["top_attr_data"],
                )
            )

            final_itinerary = response.content if isinstance(response, AIMessage) else response
            logger.info("Successfully generated itinerary from LLM response.")
            logger.debug(f"Generated Itinerary: {final_itinerary[:1000]}")

            return {
                **state,
                "final_itinerary": final_itinerary,
            }

        except Exception as e:
            logger.exception(f"Error while generating itinerary: {e}")
            raise