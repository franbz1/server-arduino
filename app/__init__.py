from flask import Flask
from app.routes.esp32_routes import esp32_blueprint

def create_app():
    app = Flask(__name__)
    app.register_blueprint(esp32_blueprint)
    return app
