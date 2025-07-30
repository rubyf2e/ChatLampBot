import azure.cognitiveservices.speech as speechsdk
import librosa
import uuid
import os

class AzureSpeechService:
    config = None
    upload_folder = None
    SPEECH_KEY = None
    SERVICE_REGION = None
    
    def __init__(self, config, upload_folder='static/speech'):
        self.config = config
        self.upload_folder = upload_folder
        self.SPEECH_KEY = self.config["AzureSpeech"]["Key"]
        self.SERVICE_REGION = self.config["AzureSpeech"]["Region"]

    def synthesize(self, user_input, target_language):
        map_languages = {
            "en":"en-US-ChristopherNeural",
            "ja":"ja-JP-AoiNeural",
            "ko":"ko-KR-GookMinNeural",
            "th":"th-TH-NiwatNeura",
            "zh-Hant": "zh-TW-HsiaoChenNeural"
            }
        
        filename = f'speech_{target_language}_{uuid.uuid4().hex}.mp3'
        filename2 = f'speech_{target_language}.mp3'
        path= f"{self.upload_folder}/{filename}"
        self.delete_file(filename2)
       
        speech_config = speechsdk.SpeechConfig(subscription=self.SPEECH_KEY, region=self.SERVICE_REGION)
        speech_config.speech_synthesis_voice_name = map_languages[target_language]
        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True, filename=path)
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        speech_synthesizer = self.set_ssml(speech_synthesizer, user_input, target_language)
        result = speech_synthesizer.speak_text_async(user_input).get()
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            librosa.load(path)
            audio_duration = round(librosa.get_duration(path=path) * 1000)
            self.rename_file(filename, filename2)
            return audio_duration
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
                
        return None
    
    def delete_file(self, filename):
        path = os.path.join(self.upload_folder, filename)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def rename_file(self, old_filename, new_filename):
        old_path = os.path.join(self.upload_folder, old_filename)
        new_path = os.path.join(self.upload_folder, new_filename)
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            return True
        return False

    #https://speech.microsoft.com/portal/voicegallery
    def ssml_string(self, text, lang="zh-TW", name="zh-TW-HsiaoChenNeural", style_name="chat", style_degree="2"):
        return """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="{lang}">
        <voice name="{name}">
            <mstts:express-as style="{style_name}" styledegree="{style_degree}">
                """ + text + """
            </mstts:express-as>
        </voice>
    </speak>"""
    
    def set_ssml(self, speech_synthesizer, text, lang, style_name="calm", style_degree="2"):
        speech_synthesizer.speak_ssml_async(self.ssml_string(lang, text))
        
        return speech_synthesizer


