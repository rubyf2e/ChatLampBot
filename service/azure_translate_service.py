from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential

class AzureTranslateService:
    def __init__(self, config):
        self.config = config
        self.text_translator = TextTranslationClient(
            credential=AzureKeyCredential(config["AzureTranslator"]["Key"]),
            endpoint=config["AzureTranslator"]["EndPoint"],
            region=config["AzureTranslator"]["Region"],
        )
        self.transliterate_map = {'zh-Hant': 'Hant', 'ja': 'Jpan', 'ko': 'Kore', 'th': 'Thai'}

    # Japanese ja
    # Korean ko
    # Thai th
    # [Lab] 雙向翻譯(日/韓/泰)
    # 輸入中文 -> 日文、英文
    # 輸入日文 -> 中文、英文
    # Chinese (Traditional) zh-Hant
    # 輸入其他語言 -> 中文、日文
    def translate(self, user_input):
        if not user_input or user_input.strip() == "":
            return "請輸入要翻譯的文字。", {}
        
        
        target_languages = ["en", "ja", "ko", "th", "zh-Hant"]
        map_languages = {"en":{"zh-Hant", "ja"}, "ja":{"zh-Hant", "en"}, "ko":{"zh-Hant", "ja"}, "th":{"zh-Hant", "ja"}, "zh-Hant":{"en", "ja"}}
        
        input_text_elements = [user_input]
        response = self.text_translator.translate(
            body=input_text_elements, to_language=target_languages
        )
        
        text = ''
        text_dict = {}
        if response and len(response) > 0:
            translation = response[0]
            detected_language = translation['detectedLanguage']['language']
            detected_language = 'zh-Hant' if detected_language == 'zh-Hans' else detected_language
            
            if translation and translation.translations and len(translation.translations) > 0:
                for item in translation.translations:
                    for map_item in map_languages[detected_language]:
                        if map_item == item['to']:
                            text += '</br>' + item['text']
                            text_dict[item['to']] = item['text']
                            if item['to'] in self.transliterate_map.keys():
                                transliterate_text = self.transliterate(item['text'], item['to'])
                                text += '</br>' + transliterate_text
                return text, text_dict
        return "翻譯失敗，請稍後再試。", text_dict


    # Chinese (Traditional)	zh-Hant	Chinese Traditional Hant	<-->	Latin Latn
    # Japanese				ja		Japanese            Jpan	<-->	Latin Latn
    # Korean				ko		Korean              Kore	<-->	Latin Latn
    # Thai					th		Thai                Thai	 -->	Latin Latn
    def transliterate(self, input_text_elements, language, to_script="Latn"):
        from_script = self.transliterate_map[language]
        response = self.text_translator.transliterate(
            body=[input_text_elements],
            language=language,
            from_script=from_script,
            to_script=to_script,
        )
        transliteration = response[0] if response else ''
        return transliteration.text if transliteration and hasattr(transliteration, 'text') else ''
