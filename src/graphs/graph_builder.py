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

    def create_travel_planner_agent_graph(self):
        logger.info("Building travel planner state graph...")

        attr_nodes = AttractionNodes(self.llm)
        hotel_nodes = HotelNodes(self.llm)
        flight_nodes = FlightNodes(self.llm)
        user_nodes = UserNodes(self.llm)
        itinerary_nodes = ItineraryNodes(self.llm)

        logger.info("Adding nodes to the state graph")
        self.graph_builder.add_node("fetch_user_data", user_nodes.parse_user_input)
        self.graph_builder.add_node("fetch_flight_data", flight_nodes.fetch_flight_data)
        self.graph_builder.add_node("summarize_flight_data", flight_nodes.summarize_flight_data)
        self.graph_builder.add_node("fetch_hotel_data", hotel_nodes.fetch_hotel_data)
        self.graph_builder.add_node("summarize_hotel_data", hotel_nodes.summarize_hotel_data)
        self.graph_builder.add_node("fetch_attr_data", attr_nodes.fetch_attr_data)
        self.graph_builder.add_node("summarize_attr_data", attr_nodes.summarize_attr_data)
        self.graph_builder.add_node("generate_itinerary", itinerary_nodes.generate_itinerary)

        logger.info("Setting entry point and transitions between nodes")
        self.graph_builder.set_entry_point("fetch_user_data")
        self.graph_builder.add_edge("fetch_user_data", "fetch_flight_data")
        self.graph_builder.add_edge("fetch_user_data", "fetch_hotel_data")
        self.graph_builder.add_edge("fetch_user_data", "fetch_attr_data")
        self.graph_builder.add_edge("fetch_hotel_data", "summarize_hotel_data")
        self.graph_builder.add_edge("fetch_flight_data", "summarize_flight_data")
        self.graph_builder.add_edge("fetch_attr_data", "summarize_attr_data")
        self.graph_builder.add_edge("summarize_flight_data", "generate_itinerary")
        self.graph_builder.add_edge("summarize_hotel_data", "generate_itinerary")
        self.graph_builder.add_edge("summarize_attr_data", "generate_itinerary")
        self.graph_builder.add_edge("generate_itinerary", END)

        logger.info("State graph build completed successfully ✅")

    def setup_graph(self):
        """
        Sets up and compiles the travel planner graph.
        """
        logger.info("Setting up state graph for travel planner agent")

        self.create_travel_planner_agent_graph()
        graph = self.graph_builder.compile()

        logger.info("Graph compiled successfully ✅")
        return graph  # optional: return image as well if needed