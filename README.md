# travel-planner-ai-agent
It is a flask API. I provides below routes and trigger an AI Agent.
This AI agent receives coordinates of source location and destination location
It then finds the weather detail of the source location using open-meteo.com API
It then finds the traffic and incident details between source and destination using TOMTOM API
It then utilizes hugging face model to generate the response

# Exposed API

http://127.0.0.1:5000/travel_plans?source_lat=13.1195&source_long=77.5837&destination_lat=12.2958&destination_long=76.6394

You need to use .env file with following data:

# .ENV

HF_API_TOKEN=Your_HuggingFace_Token

HF_MODEL_ID=mistralai/Mixtral-8x7B-Instruct-v0.1

TOMTOM_API_KEY=Your_TOMTOM_API_KEY

REQUEST_TIMEOUT_SECONDS=25

LOG_LEVEL=INFO

# Run in localhost

python app.py

# Python version: 
3.10.0