from azure.ai.language.conversations import ConversationAnalysisClient
from azure.core.credentials import AzureKeyCredential


class AzureAnalyzeConversationService:
    config = None
    ENDPOINT = None
    KEY = None
    PROJECT_NAME = None
    DEPLOYMENT_NAME = None
    client = None

    def __init__(self, config):
        self.config = config
        self.ENDPOINT = config["AzureCLU"]["END_POINT"]
        self.KEY = config["AzureCLU"]["KEY"]
        self.PROJECT_NAME = config["AzureCLU"]["PROJECT_NAME"]
        self.DEPLOYMENT_NAME = config["AzureCLU"]["DEPLOYMENT_NAME"]
        self.client = ConversationAnalysisClient(self.ENDPOINT, AzureKeyCredential(self.KEY))
        

    def analyze_conversation(self, user_input):
        with self.client:
            query = user_input
            result = self.client.analyze_conversation(
                task={
                    "kind": "Conversation",
                    "analysisInput": {
                        "conversationItem": {
                            "participantId": "1",
                            "id": "1",
                            "modality": "text",
                            "language": "zh-tw",
                            "text": query,
                        },
                        "isLoggingEnabled": False,
                    },
                    "parameters": {
                        "projectName": self.PROJECT_NAME,
                        "deploymentName": self.DEPLOYMENT_NAME,
                        "verbose": True,
                    },
                }
            )
            
            topIntent = result['result']['prediction']['topIntent']
            entities = result["result"]["prediction"]["entities"]
            
            return topIntent, entities
      