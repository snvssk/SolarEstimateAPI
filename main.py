from flask import Flask, render_template,Response
import json
import flask
app = Flask(__name__)

#Import Classes 
from Locations import Locations
from Housetype import Housetype
from Solarenergy import Solarenergy


#Example Route
@app.route('/locations')
def locations():
    location_obj = Locations()
    result = location_obj.get()
    return result

#House Type and Satellite Image Fetcher
@app.route('/housetype',methods = ['POST', 'GET'])
def housetype():
    housetype_obj = Housetype()
    if(flask.request.method=='POST'):
        result = housetype_obj.post()
    else:
        result = housetype_obj.get()
    return Response(result,mimetype='application/json')

#Solar Energy Calculator
@app.route('/solarenergy')
def solarenergy():
    solarenergy_obj = Solarenergy()
    result = solarenergy_obj.get()
    return result

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)