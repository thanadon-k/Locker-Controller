from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_cors import CORS
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
import json
from dotenv import load_dotenv
import os

MQTT_BROKER = "172.20.10.7" 
MQTT_PORT = 1883
MQTT_OPEN_ALL = "locker/open_all"
MQTT_LOCKERS = "lockers"

mqtt_client = mqtt.Client()

# data in lockers = {"name": "Microcontroller LAB", "availablecompartment": [{"compartment": "1", "status": "close"}], "time": "18:43", "date": "20/2/2025", "token": "eZGUlpjLx99thW87s"}
lockers = [{"name": "Microcontroller LAB", "availablecompartment": [{"compartment": "1", "status": "close"}], "time": "18:43", "date": "20/2/2025", "token": "eZGUlpjLx99thW87s"}]

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker!" if rc == 0 else f"Failed to connect, return code {rc}")
    client.subscribe(MQTT_LOCKERS)

def on_message(client, userdata, msg):
    if msg.topic == 'lockers' : 
        ret = json.loads(msg.payload.decode()) 
        ret["availablecompartment"] = [{"compartment": compartment, "status": "close"} for compartment in ret["availablecompartment"].split(',')]
        
        for compartment in ret["availablecompartment"]:
            client.subscribe(f"{ret['token']}/+/{compartment['compartment']}/status")
            
        lockers.append(ret) 
    
    status_parts = msg.topic.split('/')
    if len(status_parts) == 4 and status_parts[3] == "status":
        for locker in lockers:
            if locker["token"] == status_parts[0]: 
                for compartment in locker["availablecompartment"]:
                    if compartment["compartment"] == status_parts[2]: 
                        compartment["status"] = msg.payload.decode().lower()
                        break 
                   
    socketio.emit('data_update', {'value': lockers})    
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()
        
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

dotenv_path = os.path.join(os.path.dirname(__file__), "static/.env")
load_dotenv(dotenv_path)
app.secret_key = os.getenv("SECRET_KEY")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id, password):
        self.id = id
        self.password = password
        
users = {
    "forservice": User("forservice", "forservice")  
}
    
@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

@app.route("/login", methods=["GET", "POST"])   
def login():
    if request.method == "POST":
        username = request.form.get("username") 
        password = request.form.get("password")

        user = users.get(username)
        if user and user.password == password: 
            login_user(user)
            return redirect(url_for("controller"))
        else:
            flash("Invalid username or password", "danger")

    return render_template('login.html')

@app.route('/controller', methods=['GET', 'POST'])
@login_required 
def controller():
    return render_template('controller.html', lockers=lockers)

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route('/publish', methods=['POST'])
@login_required
def publish():
    data = request.get_json()
    token = data.get("token")

    if not token:
        return jsonify({"error": "Token is required"}), 400
  
    mqtt_client.publish(MQTT_OPEN_ALL, token)
    return jsonify({"message": f"Published to {MQTT_OPEN_ALL}"}), 200


@app.after_request
def prevent_back_after_logout(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5001, debug=True)


