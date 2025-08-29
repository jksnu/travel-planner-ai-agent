from pydantic import BaseModel

class CurrentWeather(BaseModel):
    temperature: str
    windspeed: str
    winddirection: str
    precipitation_probability: list
    relative_humidity_2m: list
    cloudcover: list
    precipitation_probability_unit: str = "%"
    relative_humidity_2m_unit: str = "%"
    cloudcover_unit: str = "%"      

class TrafficDetails(BaseModel):
    route: str
    distance: float
    duration: float
    traffic_speed: float
    traffic_delay: float
    traffic_congestion_level: str
    traffic_incidents: list = []

class AgentState(BaseModel):
    current_weather: CurrentWeather | None = None
    traffic_details: TrafficDetails | None = None
    source_lat: float
    source_long: float
    destination_lat: float
    destination_long: float
    result: dict | None = None