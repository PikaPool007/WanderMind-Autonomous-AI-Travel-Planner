from typing_extensions import TypedDict, List
from langgraph.graph.message import add_messages
from typing import Annotated


class AttractionsState(TypedDict):
    all_attr_data: str
    top_attr_data: str

class FlightsState(TypedDict):
    all_flight_data: str
    top_flight_data: str

class HotelsState(TypedDict):
    all_hotel_data: str
    top_hotel_data: str

class TravelPlanState(TypedDict):
    user_data: dict[str, str]
    flights: FlightsState
    hotels: HotelsState
    attractions: AttractionsState
    final_itinerary: str