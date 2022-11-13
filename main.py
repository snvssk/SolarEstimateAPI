

from flask import Flask, render_template
import json
app = Flask(__name__)

from Users import Users
from Locations import Locations
from Housetype import Housetype

@app.route('/users')
def users():
    user_obj = Users()
    result = user_obj.get()
    return result

@app.route('/locations')
def locations():
    location_obj = Locations()
    result = location_obj.get()
    return result

@app.route('/housetype')
def housetype():
    housetype_obj = Housetype()
    result = housetype_obj.get()
    return result

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)