import requests
import sys
from utils.url_helper import get_url_helper

class LightService:
    WEBHOOK_URL = None
    
    def __init__(self, config):
        self.config = config
        url_helper = get_url_helper(config)
        base_urls = url_helper.get_base_urls()
        self.WEBHOOK_URL = base_urls["WEBHOOK_URL"]
        
    # 當燈泡狀態改變時，主動推送給前端
    def notify_light_state(self, inputValue = "燈泡狀態改變"):
        try:
            payload = {"inputValue": inputValue} 
            requests.post(self.WEBHOOK_URL+"/webhook/notify_light_state", json=payload)
        except Exception as e:
            print(f"通知 SocketIO 失敗: {e}")
            sys.stdout.flush()
    

class LightState:
    value = "關"  # 預設燈泡狀態
    notify_light_function = None
    
    @classmethod
    def set_notify_light_function(cls, fun):
        cls.notify_light_function = fun

    @classmethod
    def turn_on(cls, inputValue = "turn_on"):
        cls.value = "開"
        cls.notify_light_function(inputValue)


    @classmethod
    def turn_off(cls, inputValue = "turn_off"):
        cls.value = "關"
        cls.notify_light_function(inputValue)
        
    @classmethod
    def toggle(cls, inputValue = ""):
        if cls.value == "關":
            cls.value = "開"
        elif cls.value == "開":
            cls.value = "關" 
                   
        cls.notify_light_function(inputValue)

    @classmethod
    def get_state(cls):
        return cls.value

