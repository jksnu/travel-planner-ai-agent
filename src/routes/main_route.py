from flask import Blueprint, current_app, jsonify, request
from src.agent import today_travel_plan

import logging
logger = logging.getLogger(__name__)

main_route = Blueprint('main_route', __name__)

@main_route.route('/')
def home():
    return jsonify({"message": "Welcome to the Daily Travel Agent!"})

@main_route.route('/about')
def about():
    return jsonify({"message": f"This is the about page of the Daily Travel Agent. {current_app.config['HF_MODEL_ID']}"})

@main_route.route('/travel_plans')
def travel_plans():
    try:
        source_lat = request.args.get('source_lat', type=float, default=13.1195)
        source_long = request.args.get('source_long', type=float, default=77.5837)
        destination_lat = request.args.get('destination_lat', type=float, default=13.1195)
        destination_long = request.args.get('destination_long', type=float, default=77.5837)

        travel_plan = today_travel_plan(source_lat, source_long, destination_lat, destination_long)
        return jsonify({"message": travel_plan})
    except Exception as e:
        logger.error(f"Error fetching travel plans: {e}")
        return jsonify({"error": "Failed to fetch travel plans"}), 500 