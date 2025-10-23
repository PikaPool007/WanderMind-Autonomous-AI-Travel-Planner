# src/nodes/user_nodes.py
import logging
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from src.state.state import TravelPlanState
from src.tools.logger import logger

class UserDetails(BaseModel):
    origin_city: str | None = Field(None, description="Starting city if mentioned")
    destination_city: str = Field(..., description="City where the user wants to go")
    departure_date: str | None = Field(None, description="Departure date in YYYY-MM-DD format, if mentioned")
    return_date: str | None = Field(None, description="Return date in YYYY-MM-DD format, if mentioned")
    num_days: int | None = Field(None, description="Duration of trip in days, if mentioned")
    num_travelers: int = Field(1, description="Number of people traveling, inferred from text")
    budget: str | None = Field(None, description="Budget if mentioned")
    preferences: str | None = Field(None, description="Trip type (relaxing, adventurous, cultural, etc.)")


class UserNodes:
    def __init__(self, llm):
        self.llm = llm
        logger.info("Initialized UserNodes with provided LLM instance.")

    def fetch_user_data(self, state: TravelPlanState):
        """
        Extract structured travel details from user's free-text input using the LLM.
        Output is stored in state['user_data'] as a dict.
        """
        user_message = state.get("user_data", "")
        logger.info("Starting user data extraction process.")
        logger.debug(f"Raw user message: {user_message}")

        if not user_message:
            logger.warning("No user message found in state; returning empty user_data.")
            return {"user_data": {}}

        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a travel assistant that extracts structured trip details from casual user text.

            Rules:
            - If a city is mentioned like "to Delhi", map it to destination_city.
            - If origin city is not mentioned, leave origin_city blank.
            - If the user mentions "for X days", infer num_days (and leave exact dates blank).
            - If user mentions "with 2 friends", infer num_travelers = 3.
            - If budget or preferences are described (e.g. leisure, cultural, adventure), capture them.
            - Return all fields according to the schema.
            """),
            ("human", "User message:\n{user_message}")
        ])

        structured_llm = self.llm.with_structured_output(UserDetails)
        logger.debug("Structured LLM instance created with UserDetails schema.")

        try:
            messages = prompt.format_messages(user_message=user_message)
            logger.info("Prompting LLM for user detail extraction.")
            logger.debug(f"Prompt Messages: {messages}")

            user_details = structured_llm.invoke(messages)
            logger.info("Successfully received structured user details from LLM.")
            logger.debug(f"Extracted details: {user_details}")

            user_data = user_details.dict()
            logger.info("User data successfully extracted and parsed.")
        except Exception as e:
            logger.exception(f"Error extracting user details: {e}")
            user_data = {}

        logger.info("✅ USER DATA EXTRACTION COMPLETED")
        return {"user_data": user_data}
