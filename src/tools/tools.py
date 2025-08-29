import logging
import requests
from flask import current_app
from langchain_core.tools import tool
from ..model import AgentState, CurrentWeather, TrafficDetails
from ..llm import query_llm
import json

logger = logging.getLogger(__name__)

# @tool(description="Get the current weather for a given location.")
def get_current_weather(input_params: AgentState) -> AgentState :
    try:
        source_lat = input_params.source_lat
        source_long = input_params.source_long
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={source_lat}&longitude={source_long}&current_weather=true"
            f"&hourly=relative_humidity_2m,precipitation_probability,cloudcover"
        )
        response = requests.get(url, timeout=25, verify=False)
        if response.status_code != 200:
            logger.error(f"Failed to fetch weather data: {response.status_code}")
            input_params.current_weather = None
            return input_params
        data = response.json()

        current_weather_unit = data.get("current_weather_units", {})
        current_weather  = data.get("current_weather", {})
        precipitation_probability = data.get("hourly", {}).get("precipitation_probability", [])
        relative_humidity_2m = data.get("hourly", {}).get("relative_humidity_2m", [])
        cloudcover = data.get("hourly", {}).get("cloudcover", [])
        precipitation_probability_unit = "%"
        relative_humidity_2m_unit = "%"
        cloudcover_unit = "%"
        current_weather = CurrentWeather(
            temperature = f"{current_weather.get('temperature')} {current_weather_unit.get('temperature')}",
            windspeed = f"{current_weather.get('windspeed')} {current_weather_unit.get('windspeed')}",
            winddirection = f"{current_weather.get('winddirection')} {current_weather_unit.get('winddirection')}",
            precipitation_probability = precipitation_probability,
            relative_humidity_2m = relative_humidity_2m,
            cloudcover = cloudcover,
            precipitation_probability_unit = precipitation_probability_unit,
            relative_humidity_2m_unit = relative_humidity_2m_unit,
            cloudcover_unit = cloudcover_unit  
        )    
        input_params.current_weather = current_weather
        return input_params    
    except Exception as e:
        logger.error(f"Error fetching today's weather: {e}")
        input_params.current_weather = None
        return input_params
    
# @tool(description="Get the current traffic details between source and destination.")
def get_current_traffic(input_params: AgentState) -> AgentState:
    try:
        # Step 1: Get Route
        API_KEY = current_app.config['TOMTOM_API_KEY']
        source_lat = input_params.source_lat
        source_long = input_params.source_long
        destination_lat = input_params.destination_lat
        destination_long = input_params.destination_long
        start = f"{source_lat},{source_long}"
        end = f"{destination_lat},{destination_long}"

        base_url = "https://api.tomtom.com/routing/1/calculateRoute"
        url = f"{base_url}/{start}:{end}/json"

        params = {
            "key": API_KEY,
            "traffic": "true",  # enable live traffic
        }

        resp = requests.get(url, params=params, verify=False, timeout=50)
        resp.raise_for_status()
        result = resp.json()

        # Parse response
        route_summary = result["routes"][0]["summary"]
        traffic_info = result["routes"][0].get("traffic", {})

        traffic_detail = TrafficDetails(
            route=f"{start} → {end}",
            distance=route_summary.get("lengthInMeters", 0) / 1000,  # km
            duration=route_summary.get("travelTimeInSeconds", 0) / 60,  # minutes
            traffic_speed=route_summary.get("trafficSpeed", 0),
            traffic_delay=route_summary.get("trafficDelayInSeconds", 0) / 60,  # minutes
            traffic_congestion_level=traffic_info.get("congestionLevel", "unknown"),
            traffic_incidents=[
                inc.get("description", "unknown incident")
                for inc in result["routes"][0].get("legs", [])[0].get("points", [])
                if "incident" in inc
            ]
        )
        input_params.traffic_details = traffic_detail
        return input_params

    except Exception as e:
        logger.error(f"Error fetching traffic detail: {e}")
        input_params.traffic_details = None
        return input_params

# @tool(description="Summarise the travel plan based on weather and traffic details using LLM.")
def summarise_travel_plan_llm(agent_state: AgentState) -> AgentState:
    try:
        SYSTEM_PROMPT = (
            """You are a travel assistant. Based on the current weather and traffic details, 
            provide a concise summary for today's travel plan. 
            Your travel plan must follow the below format strictly:
            The travel plan must be a JSON data with following keys and convert latitude and longitude to address using any geocoding service.
            1. Weather-Summary: A brief overview of the current weather conditions. 
            2. Traffic-Summary: A brief overview of the current traffic conditions.
            3. Travel-Time: Suggest the best time to start the journey based on weather and traffic conditions.
            4. Estimated-Travel-Time: Provide the estimated travel time considering current traffic conditions.
            5. Recommendations: Any recommendations or precautions for the journey based on weather and traffic.            
            Remeber, the response must be a valid JSON data only and nothing else.
            """
        )

        USER_PROMPT = (
            f"""I am thinking to travel from (latitude, longitude = {agent_state.source_lat}, {agent_state.source_long} to (latitude, longitude = {agent_state.destination_lat}, {agent_state.destination_long})
                In final response, convert these latitude and longitude to address using any geocoding service.
                Do not provide any latitude and longitude and any bracket in the response.
                Today's weather and traffic details are as follows:\n
                Weather: {agent_state.current_weather.model_dump_json() if agent_state.current_weather else 'No data available'}\n
                Traffic Details: {agent_state.traffic_details.model_dump_json() if agent_state.traffic_details else 'No data available'}\n
                Please provide a concise travel plan strictly in JSON format as mentioned in the system prompt.
            """
        )
        summary = query_llm([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT}
        ])
        if summary is not None:
            summary_json = json.loads(summary)
        else:
            summary_json = None
        agent_state.result = summary_json
        return agent_state 

    except Exception as e:
        logger.error(f"Error summarizing travel plan: {e}")
        agent_state.result = None
        return agent_state