import eventlet
eventlet.monkey_patch()

from flask import Flask, request
from flask_socketio import SocketIO
import requests
import configparser


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
config = configparser.ConfigParser()
config.read("config.ini")
API_URL = config["Base"]["API_URL"]

@app.route("/", methods=["GET"])
def index():
    return "Chat Lamp Bot is running!"

@app.route("/webhook/notify_light_state", methods=["POST"])
def webhook_notify_light_state():
    input_value = request.json.get("inputValue", "")
    notify_light_state(input_value)
    return "OK", 200

def get_light_status():
    try:
        response = requests.get(API_URL+"/light_status")
        if response.status_code == 200:
            return response.json()["state"]
        else:
            return "未知"
    except Exception as e:
        print(e)
        return "錯誤"
    
def toggle_light_state():
    try:
        response = requests.get(API_URL+"/toggle_light_state")
        if response.status_code == 200:
            return response.json()["state"]
        else:
            return "未知"
    except Exception as e:
        print(e)
        return "錯誤"

@socketio.on('get_light_state')
def handle_get_light_state():
    print("燈泡狀態")
    notify_light_state()
    
@socketio.on('toggle_light_state')
def handle_toggle_light_state():
    print("燈泡狀態請求已處理")
    toggle_light_state()


# 當燈泡狀態改變時，主動推送給前端
def notify_light_state(inputValue = '燈泡狀態請求已處理'):
    state = get_light_status()
    print("燈泡狀態請求已處理-"+state)
    socketio.emit('light_state', {'state': state, 'inputValue': inputValue})
    
if __name__ == "__main__":
    socketio.run(app, port=5004, debug=True, host='127.0.0.1')
    
    
import command.weather