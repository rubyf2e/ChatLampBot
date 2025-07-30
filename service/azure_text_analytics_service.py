from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential


class AzureTextAnalyticsService:
    config = None
    client = None
    
    def __init__(self, config):
        self.config = config
        self.client = TextAnalyticsClient(config["AzureTextAnalyticsClient"]["END_POINT"], AzureKeyCredential(config["AzureTextAnalyticsClient"]["Key"]))

        
    def text_analytics(self, user_input):
        document = [{'id':'1','text':user_input}]
        detect_language_response = self.client.detect_language(document)[0]
        detected_language = detect_language_response.primary_language
        languageId = detected_language.iso6391_name
        
        document = [{'id':'1','text':user_input,'language':languageId}]
        extract_key_phrases_response = self.client.extract_key_phrases(document)[0]
        key_phrases = extract_key_phrases_response.key_phrases
        
        analyze_sentiment_response = self.client.analyze_sentiment(document)[0]
        sentiment = analyze_sentiment_response.sentiment
        confidence_scores = analyze_sentiment_response.confidence_scores
        
        return languageId, key_phrases, sentiment, confidence_scores
