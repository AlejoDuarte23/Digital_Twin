from flask import Flask, jsonify, render_template
from flask_cors import CORS
import json
import pickle

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gps')
def gps():
    return render_template('gps.html')

@app.route('/truck_data', methods=['GET'])
def truck_data():
    with open('set_up_2_3_4_.json', 'r') as file:
        data = json.load(file)
    return jsonify(data)

@app.route('/data', methods=['GET'])
def gps_data():
    #with open('gps_st_2_3_4.pkl', 'rb') as file:
        #loaded_dict = pickle.load(file)
    with open('gps_st_2_3_4_2.geojson', 'r') as file:
        data2 = json.load(file)
    return jsonify(data2)
 

if __name__ == '__main__':
    app.run(port=8888,debug=True)
