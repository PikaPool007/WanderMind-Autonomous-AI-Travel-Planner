import logging
from src.main import load_travel_planner_agent
from src.tools.logger import logger  # Shared logger import


if __name__ == "__main__":
    logger.info("Application started.")
    try:
        load_travel_planner_agent()
        logger.info("Application executed successfully.")
    except Exception as e:
        logger.exception("Application terminated with an error: %s", str(e))
    finally:
        logger.info("Application shutdown.")