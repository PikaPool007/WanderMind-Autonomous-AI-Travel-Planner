from langgraph.graph import StateGraph, END
from IPython.display import display, Image

from src.state.state import TravelPlanState
from src.nodes.attr_nodes import AttractionNodes
from src.nodes.hotels_nodes import HotelNodes
from src.nodes.flights_nodes import FlightNodes
from src.nodes.user_nodes import UserNodes
from src.nodes.itineary_nodes import ItineraryNodes

from src.tools.logger import logger


class GraphBuilder:
    def __init__(self, model):
        self.llm = model
        self.graph_builder = StateGraph(TravelPlanState)
        logger.info("GraphBuilder initialized with provided LLM model")

    def travel_planner_agent_build_graph(self):
        logger.info("Building travel planner state graph...")

        attr_nodes = AttractionNodes(self.llm)
        hotel_nodes = HotelNodes(self.llm)
        flight_nodes = FlightNodes(self.llm)
        user_nodes = UserNodes(self.llm)
        itinerary_nodes = ItineraryNodes(self.llm)

        logger.info("Adding nodes to the state graph")
        self.graph_builder.add_node("fetch_user_data", user_nodes.fetch_user_data)
        self.graph_builder.add_node("get_flight_details", flight_nodes.get_flight_data)
        self.graph_builder.add_node("get_top_flight_details", flight_nodes.get_top_flight_summary)
        self.graph_builder.add_node("get_hotel_details", hotel_nodes.get_hotel_data)
        self.graph_builder.add_node("get_top_hotel_details", hotel_nodes.get_top_hotels)
        self.graph_builder.add_node("get_attr_details", attr_nodes.get_attr_details)
        self.graph_builder.add_node("get_top_attr_details", attr_nodes.get_top_attr_details)
        self.graph_builder.add_node("get_itineary", itinerary_nodes.get_itinerary)

        logger.info("Setting entry point and transitions between nodes")
        self.graph_builder.set_entry_point("fetch_user_data")
        self.graph_builder.add_edge("fetch_user_data", "get_flight_details")
        self.graph_builder.add_edge("fetch_user_data", "get_hotel_details")
        self.graph_builder.add_edge("fetch_user_data", "get_attr_details")
        self.graph_builder.add_edge("get_hotel_details", "get_top_hotel_details")
        self.graph_builder.add_edge("get_flight_details", "get_top_flight_details")
        self.graph_builder.add_edge("get_attr_details", "get_top_attr_details")
        self.graph_builder.add_edge("get_top_flight_details", "get_itineary")
        self.graph_builder.add_edge("get_top_hotel_details", "get_itineary")
        self.graph_builder.add_edge("get_top_attr_details", "get_itineary")
        self.graph_builder.add_edge("get_itineary", END)

        logger.info("State graph build completed successfully ✅")

    def setup_graph(self):
        """
        Sets up and compiles the travel planner graph.
        """
        logger.info("Setting up state graph for travel planner agent")

        self.travel_planner_agent_build_graph()
        graph = self.graph_builder.compile()

        logger.info("Graph compiled successfully ✅")
        return graph  # optional: return image as well if needed