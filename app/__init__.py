from flask import Flask
from app.routes import routes

def create_app():
    app = Flask(__name__)
    # app.secret_key is needed for the sessions. Not sure where else to put it.
    app.secret_key = "8db17dd2a03dffabd436f2ffbd310221ea72d45732bce22f5fc1c28b4f69101d" 
    # sets up the blueprint used in the routes
    app.register_blueprint(routes)

    return app
