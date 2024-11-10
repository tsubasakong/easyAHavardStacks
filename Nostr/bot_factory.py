from BotAPI.chatbase_bot import ChatBaseBotAPI
from BotAPI.gpt_bot import GPTBotAPI

class ChatBotFactory:
    def __init__(self, bot_type, chatbot_name, chatbot_id, api_key, source_text=None, link_array=None, temp=0.8):
        self.bot_type = bot_type
        self.chatbot_name = chatbot_name
        self.chatbot_id = chatbot_id
        self.api_key = api_key
        self.source_text = source_text
        self.link_array = link_array
        self.temp = temp

    def get_bot(self):
        if self.bot_type == 'GPT':
            return GPTBotAPI(self.chatbot_name, self.chatbot_id, self.api_key, self.temp)
        elif self.bot_type == 'ChatBase':
            return ChatBaseBotAPI(self.chatbot_name, self.chatbot_id, self.api_key, self.source_text, self.link_array, self.temp)
        else:
            raise ValueError('Invalid bot type')
