from flask import Flask
from Users import Users
from Locations import Locations

class FlaskAppWrapper(object):

    def __init__(self, app, **configs):
        self.app = app
        self.configs(**configs)

    def configs(self, **configs):
        for config, value in configs:
            self.app.config[config.upper()] = value

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, methods=['GET'], *args, **kwargs):
        self.app.add_url_rule(endpoint, endpoint_name, handler, methods=methods, *args, **kwargs)

    def run(self, **kwargs):
        self.app.run(**kwargs)

flask_app = Flask(__name__)

app = FlaskAppWrapper(flask_app)

def action():
    """ Function which is triggered in flask app """
    return "Hello World"

user_obj = Users()
locations_obj = Locations()
# Add endpoint for the action function
app.add_endpoint('/users', 'users', user_obj.get, methods=['GET'])
app.add_endpoint('/locations', 'locations', locations_obj.get, methods=['GET'])
app.add_endpoint('/action', 'action', action, methods=['GET'])

if __name__ == "__main__":
    app.run(debug=True)