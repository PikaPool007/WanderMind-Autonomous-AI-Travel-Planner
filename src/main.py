import streamlit as st
import logging

from src.ui.streamlitui.loadui import LoadStreamlitUI
from src.LLMs.openaillm import OpenAiLLM
from src.graphs.graph_builder import GraphBuilder
from src.ui.streamlitui.displayresult import DisplayResultStreamlit
from src.tools.logger import logger  # Shared logger import


def load_travel_planner_agent():
    """
    Loads and runs the LangGraph AgenticAI application with Streamlit UI.
    This function initializes the UI, handles user input, configures the LLM model,
    sets up the graph based on the selected use case, and displays the output while
    implementing exception handling for robustness.
    """
    logger.info("Starting travel planner agent...")

    ui = LoadStreamlitUI()
    user_inp = ui.load_streamlit_ui()
    logger.info("Streamlit UI loaded successfully.")

    user_msg = st.chat_input("Enter your message:")
    if user_msg:
        logger.info("User input received: %s", user_msg)
        try:
            model = OpenAiLLM.get_llm_model()
            if not model:
                logger.error("Failed to load LLM model.")
                st.error("Error: Failed to load LLM model.")
                return

            logger.info("LLM model loaded successfully.")
            graph_builder = GraphBuilder(model)

            try:
                graph = graph_builder.setup_graph()
                logger.info("Graph setup completed successfully.")
                # st.image(img, caption="Generated Graph")
                DisplayResultStreamlit(graph, user_msg).display_result_on_ui()
                logger.info("Result displayed successfully on Streamlit UI.")
            except Exception as e:
                logger.exception("Error while setting up graph: %s", str(e))
                st.error(f"Error: Failed to set up graph: {str(e)}")
                return

        except Exception as ex:
            logger.exception("Unexpected error during travel planner execution: %s", str(ex))
            st.error(f"Error: Failed: {str(ex)}")
            return

    logger.info("Travel planner agent execution completed.")
