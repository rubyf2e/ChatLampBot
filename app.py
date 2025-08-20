import json 
import configparser
import sys
from flask import Flask, request, abort, render_template
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    AudioMessage
)

from service.chat_service import ChatService
from service.light_service import LightService, LightState
from service.azure_speech_service import AzureSpeechService
from service.azure_translate_service import AzureTranslateService
from service.azure_text_analytics_service import AzureTextAnalyticsService
from service.azure_analyze_conversation_service import AzureAnalyzeConversationService
from service.light_chat_service import LightChatService
from service.weather_service import WeatherService
from utils.url_helper import get_url_helper


config = configparser.ConfigParser()
config.read("config.ini")

# 初始化 URL 管理器
url_helper = get_url_helper(config)

app = Flask(__name__)
UPLOAD_FOLDER = config["Base"]["UPLOAD_FOLDER"]
channel_access_token = config["Line"]["CHANNEL_ACCESS_TOKEN"]
channel_secret = config["Line"]["CHANNEL_SECRET"]
handler = WebhookHandler(channel_secret)
configuration = Configuration(access_token=channel_access_token)

azure_speech_service = AzureSpeechService(config, UPLOAD_FOLDER)
azure_translate_service = AzureTranslateService(config)
azure_text_analytics_service = AzureTextAnalyticsService(config)
azure_analyze_conversation_service = AzureAnalyzeConversationService(config)
weather_service = WeatherService(config)

chat_service = ChatService(config)
light_service = LightService(config)

light_state = LightState()
light_state.set_notify_light_function(light_service.notify_light_state)
light_chat_service = LightChatService(azure_analyze_conversation_service, light_state, chat_service)

@app.route("/", methods=["GET"])
def index():
    base_urls = url_helper.get_base_urls()
    return render_template("index.html", 
                        STATIC_URL=base_urls["STATIC_URL"],
                        AUDIO_URL=base_urls["AUDIO_URL"], 
                        API_URL=base_urls["API_URL"], 
                        WEBHOOK_PATH_URL=base_urls["WEBHOOK_PATH_URL"], 
                        WEBHOOK_URL=base_urls["WEBHOOK_URL"])

@app.route("/api/light", methods=["POST"])
def light():
    if request.method == "POST":
        data = request.form
        chinese_text = data.get("message", "")
        model = data.get("model", "azure")

        detected_language, key_phrases, sentiment, confidence_scores = azure_text_analytics_service.text_analytics(chinese_text)
        intent, entity = light_chat_service.analyze_conversation(chinese_text, model)
        
        emotion_message_text_file = "prompts/emotion_user_message_text.json"
        emotion_prompts = chat_service.get_prompts_content(emotion_message_text_file)
        message_text = chat_service.set_prompts_content(emotion_prompts, "user", "{user_input}", chinese_text)
        emotion = chat_service.azure_completions_chat_bot(chinese_text,  message_text)
        
        weather_service.set_default_opendata_cwa()
        stations_data = weather_service.get_stations_data()
        weather_message_text_file = "prompts/weather_user_message_text.json"
        weather_prompts = chat_service.get_prompts_content(weather_message_text_file)
        weather_prompts = chat_service.set_prompts_content(weather_prompts, "system", "{stations_data}", json.dumps(stations_data, ensure_ascii=False))
        message_text = chat_service.set_prompts_content(weather_prompts, "user", "{user_input}", chinese_text)
        weather = chat_service.azure_completions_chat_bot(chinese_text, message_text)
        
        if weather['is_weather_query'] == True:
            weather['location'] = weather['location'] if weather['location'] else "臺北"
            entity = weather_service.render_station_data(weather_service.get_station_weather(weather['location']))
            
            weather_message_text_file = "prompts/weather_bot_message_text.json"
            weather_prompts = chat_service.get_prompts_content(weather_message_text_file)
            message_text = chat_service.set_prompts_content(weather_prompts, "user", "{stations_data}", entity)
            entity = chat_service.azure_completions_chat(entity, '', message_text)

            
        data = {
            "chinese_text": chinese_text,
            "intent": intent,
            "entity": entity,
            "detected_language": detected_language,
            "key_phrases": key_phrases,
            "sentiment": sentiment,
            "emotion": emotion,
            "weather": weather,
            "confidence_scores": {
                "positive": confidence_scores.positive,
                "neutral": confidence_scores.neutral,
                "negative": confidence_scores.negative
            }
        }

        return data
    return {}

@app.route("/api/light_status", methods=["GET"])
def light_status():
    return {'state': light_state.get_state()}

@app.route("/api/toggle_light_state", methods=["GET"])
def toggle_light_state():
    light_state.toggle()
    return {'state': light_state.get_state()}


@app.route("/api/azure_translate", methods=["POST"])
def azure_translate():
    if request.method == "POST":
        data = request.form
        chinese_text = data["message"]
        azure_speech_service.synthesize(chinese_text, 'zh-Hant')
        translation_result, text_dict = azure_translate_service.translate(chinese_text)

        if not translation_result:
            translation_result = "翻譯失敗，請稍後再試。"
            
        for lang, text in text_dict.items():
            audio_duration = azure_speech_service.synthesize(text, lang)
        return translation_result


@app.route("/api/line/bot/callback", methods=["POST", "OPTIONS"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    
    if not signature:
        app.logger.error("Missing X-Line-Signature header")
        abort(400)
    
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError as e:
        app.logger.error(f"Invalid signature error: {e}")
        abort(400)
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        abort(500)
    
    return "OK"

@handler.add(MessageEvent, message=TextMessageContent)
def message_text(event):
    intent, entity = light_chat_service.analyze_conversation(event.message.text, "azure")
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=intent),
                          TextMessage(text=entity)],
            )
        )
    
def translate_service_message_text(event):
    def map_azure_speech(messages, translation_result, target_language):
        audio_duration = azure_speech_service.synthesize(translation_result, target_language)
        
        if audio_duration != None:
            deploy_url = url_helper.get_deploy_url()
            messages.append(AudioMessage(originalContentUrl=deploy_url+f"/static/speech_{target_language}.mp3", duration=audio_duration))
        
        return messages
    
    try:
        translation_result, text_dict = azure_translate_service. ㄒ(event.message.text)
        if not translation_result:
            translation_result = "翻譯失敗，請稍後再試。"

        messages = [TextMessage(text=translation_result)]

        for lang, text in text_dict.items():
            messages = map_azure_speech(messages, text, lang)
        
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=messages,
                )
            )
    except Exception as e:
        print(f"Error in message_text: {e}")
        sys.stdout.flush()
        # 發送錯誤訊息給用戶
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="抱歉，處理您的訊息時發生錯誤。")],
                )
            )
  
if __name__ == "__main__":
    app.run()