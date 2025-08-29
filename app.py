from flask import Flask
from src.routes.main_route import main_route
import logging
from src import config

app = Flask(__name__)
app.config.from_object(config.Config)

app.register_blueprint(main_route) 
# Set up logging
logging.basicConfig(level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    app.run(
        debug=True
    )

