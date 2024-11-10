import os
import openai

class GPTBotAPI:
    def __init__(self, chatbot_name: str,chatbot_id: str, api_key: str, temp=0.8):
        self.chatbot_name=chatbot_name
        self.chatbot_id=chatbot_id
        self.api_key=api_key
        self.temp=temp
    
    def message_chatbot(self,message):
        openai.api_key = self.api_key
        print("openai GPT Bot")
        messages = []
        system_message = {"role": "system", "content": "You are a helpful assistant."}
        messages.append(system_message)
        user_message = {"role": "user", "content": message}
        messages.append(user_message)
        # print(messages)
        # https://platform.openai.com/docs/api-reference/completions/create
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo-0613",
                                                messages=messages, temperature= self.temp)
        print("response", response)
        return {"response": response.choices[0].message["content"]}




    