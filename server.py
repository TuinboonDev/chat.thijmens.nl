from flask import Flask, render_template, request, redirect, session, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO, emit

from dotenv import load_dotenv
import asyncio
import websockets
import bcrypt
import json
import os
import re

load_dotenv()

app = Flask(__name__)
socketio = SocketIO()
socketio.init_app(app)

app.secret_key = os.getenv("APP_SECREY_KEY")

# limiter = Limiter(	
#     get_remote_address,
#     app=app
# )

from internals.get_messages import getmessages
from internals.permissions import check_general_permission
from internals.jwt import generate_access_token, generate_refresh_token, verify_token
import threading

# Testing websockets

@socketio.on("getmessages")
def checkping(data):
	if verify_token(data["access_token"]) in ["expired", "invalid"]:
		messages = []
	else:
		messages = getmessages()
	emit('messages', messages, room=request.sid) 

@app.route('/')
# @limiter.limit("1 per second")  # Rate limiting
def main():
	return render_template("index.html", data=[{"userid": "Tuinboon", "message": "ehm hi"}])

@app.route('/404')
def four_o_four():
	return "You do not have access to this or havent <a href='/login'>logged in</a> yet", 404

@app.route('/error')
def error():
	return request.args.get("error"), 400

@app.route('/login', methods=['GET'])
# @limiter.limit("5 per minute")  # Rate limiting
def login():
	return render_template("login.html")

@app.route('/api/login', methods=['POST'])
# @limiter.limit("5 per minute")  # Rate limiting
def api_login():
	print(bcrypt.gensalt().decode("utf-8"))
	if request.method == 'POST':
		data = request.json
		name = data.get("username", "")
		password = data.get("password", "").encode("utf-8")
		
		accounts = json.loads(open("accounts.json", "r").read())

		user = accounts.get(name.lower(), None)
		if user:
			stored_hashed_pw = user["pass"].encode("utf-8")
			if bcrypt.checkpw(password, stored_hashed_pw):
				access_token = generate_access_token(user["id"])
				refresh_token = generate_refresh_token(user["id"], user["token_version"])

				response = jsonify({'access_token': access_token})
				response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True, samesite='Strict')

				return response

		return jsonify({"error": "Incorrect credentials."}), 404
		
	return render_template("login.html")

@app.route('/api/register', methods=['POST'])
#@limiter.limit("5 per minute")  # Rate limiting
def api_register():
	if request.method == 'POST':
		data = request.json
		name = data.get("username").lower()
		password = bcrypt.hashpw(data.get("password").encode("utf-8"), bcrypt.gensalt())

		if not re.search(r"^[A-Za-z][A-Za-z0-9_]{3,18}$", name):
			return jsonify({"error": "Invalid username, username must be between 3-18 characters and must be alphanumeric."}), 400
		
		with open("accounts.json", "r+") as f:
			data = json.load(f)
			if name in data:
				return jsonify({"error": "Username is already in use."}), 404
			data[name] = {"pass": password.decode("utf-8"), "id": len(data.keys()), "servers": [], "token_version": 0}
			f.seek(0)
			json.dump(data, f, ensure_ascii=False, indent=4)
			f.truncate() 


		access_token = generate_access_token(len(data.keys()))
		refresh_token = generate_refresh_token(len(data.keys()), 0)

		response = jsonify({'access_token': access_token})
		response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True, samesite='Strict')

		return response
		
@app.route('/register', methods=['GET'])
def register():
	return render_template("register.html")

if __name__ == '__main__':
	app.run(debug=True)
	socketio.run(app, host="0.0.0.0", port=9000)
