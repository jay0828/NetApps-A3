#!/usr/bin/env python
from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
from flask_httpauth import HTTPBasicAuth
import led
import requests
from led import red_on, blue_on, green_on, magenta_on, yellow_on, cyan_on, white_on
import zeroconf

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'accounts'
app.config['MONGO_URI'] = 'mongodb://localhost/accounts'

mongo = PyMongo(app)

auth = HTTPBasicAuth();

@auth.get_password
def get_pw(username):
    accounts = mongo.db.accounts
    accExists = accounts.find_one({'username': username})
    if accExists:
       return accExists['password'];
    return None

@app.route('/LED')
def handleLED():
    status = request.args.get('status')
    color = request.args.get('color')
    intensity = request.args.get('intensity')
    zc = zeroconf.Zeroconf()
    info = zc.get_service_info("_http._tcp.local.", "LED PI._http._tcp.local.")
    payload = {'color': color, 'status': status, 'intensity' : intensity}
    print(color, status, intensity)
    zc = requests.get('http://172.29.81.174:800/LED', params=payload)
    led.LED()
    return None



@app.route('/accounts', methods=['GET'])
@auth.login_required
def get_all_accounts():
    accounts = mongo.db.accounts
    output = []
    for s in accounts.find():
        output.append({'username': s['username'], 'password': s['password']})
    return jsonify({'Get all accounts': output})

@app.route('/accounts/<username>', methods=['GET'])
@auth.login_required
def get_one_accounts(username):
    accounts = mongo.db.accounts
    accExists = accounts.find_one({'username': username})
    if accExists:
        output = {'username': accExists['username'], 'password': accExists['password']}
    else:
        output = "Account does not exist"
    return jsonify({'Get account': output})


@app.route('/accounts', methods=['POST'])
@auth.login_required
def add_account():
    accounts = mongo.db.accounts
    username = request.values.get('username')
    password = request.values.get('password')
    accExists = accounts.find_one({'username': username})
    if accExists:
        output = "User already exists"
    else:
        accounts.insert_one({'username': username, 'password': password})
        accExists = accounts.find_one({'username': username, 'password': password})
        if accExists:
            output = {'username': accExists['username'], 'password': accExists['password']}
        else:
            output = "Unable to create account"
    return jsonify({'Created': output})

@app.route('/accounts', methods=['PUT'])
@auth.login_required
def update_password():
    accounts = mongo.db.accounts
    username = request.values.get('username')
    password = request.values.get('password')
    accExists = accounts.find_one({'username': username, 'password': password})
    if accExists:
        accounts.update_one({'username': username}, {'$set': {'password': password}}, upsert=False)
        updated_account = accounts.find_one({'username': username, 'password': password})
        if updated_account:
            output = {'username': updated_account['username'], 'password': updated_account['password']}
        else:
            output = "Unable to update password"
    else:
        output = "Account does not exist"
    return jsonify({'Updated': output})

@app.route('/letmein')
def printIn():
    return("made it")
    
@app.route('/accounts', methods=['DELETE'])
@auth.login_required
def remove_account():
    accounts = mongo.db.accounts
    username = request.values.get('username')
    password = request.values.get('password')
    accExists = accounts.find_one({'username': username, 'password': password})
    if accExists:
        accounts.remove({'username': username, 'password': password})
        removed_account = accounts.find_one({'username': username})
        if removed_account:
            output = "Unable to delete account"
        else:
            output = {'username': username, 'password': password}
    else:
        output = "Username and password do not match or account does not exist"
    return jsonify({'Deleted': output})

if __name__ == '__main__':
    app.run(host='172.29.19.69', port=5000, debug=True)
    
