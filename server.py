from flask import Flask, render_template, request, redirect, session, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO, emit

from dotenv import load_dotenv
import asyncio
import websockets
import json
import os

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
from internals.jwt import generate_access_token, generate_refresh_token
import threading

# Testing websockets
@socketio.on("my_event")
def checkping():
	for x in range(5):
		emit('server', {"data1":x, "data":"a"}, room=request.sid)
		socketio.sleep(1)

@app.route('/')
# @limiter.limit("1 per second")  # Rate limiting
def main():
	if check_general_permission():
		messages = getmessages()
		return render_template("index.html", data=messages)
	return "You do not have access to this or havent <a href='/login'>logged in</a> yet", 404

@app.route('/login', methods=['GET', 'POST'])
# @limiter.limit("5 per minute")  # Rate limiting
def login():
	if request.method == 'POST':
		data = request.json
		name = data.get("username")
		password = data.get("password")
		
		accounts = open("accounts.json", "r").read()

		print(json.loads(accounts))
		user = json.loads(accounts)[name.lower()]
		if user["pass"] == password:
			access_token = generate_access_token(user["id"])
			refresh_token = generate_refresh_token(user["id"], user["token_version"])

			response = jsonify({'access_token': access_token})
			response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True, samesite='Strict')

			return response
		else:
			return "Incorrect credentials", 404
		
	return render_template("login.html")

if __name__ == '__main__':
	app.run(debug=True)
	socketio.run(app, host="0.0.0.0", port=9000)
