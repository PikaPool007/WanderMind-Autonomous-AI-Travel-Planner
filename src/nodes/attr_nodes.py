from pydantic import BaseModel, Field
from typing import List
from langchain_core.prompts import ChatPromptTemplate

from src.state.state import TravelPlanState
from src.LLMs.openaillm import OpenAiLLM
from src.tools.tools_for_attr import AttractionTools
from src.tools.logger import logger


class AttractionNodes:
    def __init__(self, llm):
        self.llm = llm
        logger.info("AttractionNodes initialized with LLM instance")

    def get_attr_details(self, state: TravelPlanState) -> dict:
        """
        Retrieve attraction details and store them in AttractionsState.all_attr_data.
        """
        try:
            user_data = state["user_data"]
            destination_city = user_data.get("destination_city")
            logger.info(f"Fetching attraction details for city: {destination_city}")

            tools_for_attr = AttractionTools()
            retriever = tools_for_attr.create_retriever()
            retriever_results = retriever.invoke(destination_city)
            dest_data = retriever_results[0].page_content

            logger.info(f"Retrieved attraction details for {destination_city} successfully")

            return {
                "attractions": {
                    "all_attr_data": dest_data,
                    "top_attr_data": ""
                }
            }
        except Exception as e:
            logger.exception(f"Error occurred while fetching attraction details: {e}")
            raise

    def get_top_attr_details(self, state: TravelPlanState) -> dict:
        """
        Generate top attraction recommendations based on user's travel details.
        """
        try:
            logger.info("Starting top attraction recommendations generation")

            class POIRecommendation(BaseModel):
                name: str = Field(..., description="Name of the place of interest")
                category: str = Field(..., description="Category of the attraction, e.g. Cultural, Nature, Entertainment")

            class DestinationRecommendations(BaseModel):
                recommendations: List[POIRecommendation]

            llm = self.llm.with_structured_output(DestinationRecommendations)
            logger.info("Structured LLM model prepared for top attraction recommendations")

            user_data = state["user_data"]
            dest_data = state["attractions"]["all_attr_data"]

            system = """
            You are a travel planner AI specializing in finding tourist attractions for a given set of travel details like number of days and reason of travel.

            You are provided below:
            - A list of tourist attractions for a specific city (including names, categories, and descriptions)
            - Details about the user’s trip (e.g., duration, travel reason, and preferences)

            Your goal is to generate a list of the **top recommended places to visit** for a traveler, 
            structured according to the `DestinationRecommendations` schema. 

            Guidelines:
            - Choose as many recommendations as the need be based on the user's preferences and travel time.
            - Ensure a good balance of categories (e.g., Cultural, Nature, Entertainment, Religious, Adventure, etc.) if available
            - Do not hallucinate names or places not present in `dest_data`. If fewer attractions match well, recommend only those with strong relevance.
            - Be concise, avoid repetition, and prefer quality over quantity.
            - Only select from the given data context.
            - The details provided by the user are very important and should never be ignored.
            - Output must strictly follow the `DestinationRecommendations` schema.

            List of All tourist attractions:
            {context}

            Details about the user’s trip:
            {query}
            """
            query = (
                f"Travelling to {user_data['destination_city']} for {user_data['num_days']} days "
                f"with {user_data['num_travelers']} people, my preferences are {user_data['preferences']}"
            )

            prompt = ChatPromptTemplate.from_template(system)
            get_top_results_chain = prompt | llm

            logger.info(f"Invoking LLM for top attractions in {user_data['destination_city']}")
            top_attr_details = get_top_results_chain.invoke({"context": dest_data, "query": query})

            logger.info(f"Successfully generated top attraction recommendations for {user_data['destination_city']}")

            return {
                "attractions": {
                    "all_attr_data": dest_data,
                    "top_attr_data": top_attr_details
                }
            }

        except Exception as e:
            logger.exception(f"Error while generating top attraction recommendations: {e}")
            raise