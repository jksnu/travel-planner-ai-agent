import logging
from src.tools import get_current_weather, get_current_traffic, summarise_travel_plan_llm
from ..model import AgentState
from langgraph.graph import StateGraph, END

logger = logging.getLogger(__name__)

def today_travel_plan(source_lat, source_long, destination_lat, destination_long):
    try:
        initial_state = AgentState(
            source_lat=source_lat,
            source_long=source_long,
            destination_lat=destination_lat,
            destination_long=destination_long
        )

        # Define the workflow
        workflow = StateGraph(AgentState)

        # Adding nodes to the workflow
        workflow.add_node("Get Current Weather", get_current_weather)
        workflow.add_node("Get Current Traffic", get_current_traffic)
        workflow.add_node("Summarise Travel Plan", summarise_travel_plan_llm)

        # Define the edges between nodes
        workflow.add_edge("Get Current Weather", "Get Current Traffic")
        workflow.add_edge("Get Current Traffic", "Summarise Travel Plan")
        workflow.add_edge("Summarise Travel Plan", END)

        # Set the entry point
        workflow.set_entry_point("Get Current Weather")

        # compute the workflow
        graph_app = workflow.compile()

        # Run with initial state
        graph_result = graph_app.invoke(initial_state)
        return graph_result["result"]
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise e
        
