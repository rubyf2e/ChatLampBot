
class LightChatService:
    def __init__(self, azure_analyze_conversation_service, light_state, chat_service):
        self.azure_analyze_conversation_service = azure_analyze_conversation_service
        self.light_state = light_state
        self.chat_service = chat_service

    def analyze_conversation(self, user_input, chat_model):
        topIntent, entities = self.azure_analyze_conversation_service.analyze_conversation(user_input)
        
        if topIntent:
            if topIntent == "TurnOn":
                self.light_state.turn_on()
                result_entity = f"{self.light_state.get_state()}"
            elif topIntent == "TurnOff":
                self.light_state.turn_off() 
                result_entity = f"{self.light_state.get_state()}"
            else:
                result_entity = self.chat_service.chat(user_input, chat_model)
        else:
            result_entity = self.chat_service.chat(user_input, chat_model)
        
        return topIntent, result_entity
    