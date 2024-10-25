from openai import OpenAI
from logger import LOG

class LLMChat:
    def __init__(self, model_name, system_prompt):
        self.client = OpenAI()
        self.model_name = model_name
        self.system_prompt = system_prompt
        # Check if system_prompt is a file path
        self.__load_template__(system_prompt)
        self.create_prompt_template()

    def __load_template__(self, system_prompt):
        LOG.info(f"[LLMChat][Create system prompt]{system_prompt}")
        if isinstance(system_prompt, str) and system_prompt.endswith('.txt'):
            with open(system_prompt, 'r') as file:
                content = file.read()
            self.system_prompt = content
        else:
            self.system_prompt = system_prompt
            
    def create_prompt_template(self):
        # Create a formatted prompt template using system_prompt
        messages = [
            {"role":"system","content":self.system_prompt}
        ]
        self.messages = messages

    def chat_with_llm(self, user_message, history):
        LOG.info(f"[LLMChat][Chatting]{user_message}")
        # 将历史对话和新消息转换为Langchain消息格式
        self.messages.append(
            {"role":"user","content":user_message}
        )
        # 使用Langchain进行对话
        response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.messages
            )
        
        self.messages.append(
            {"role":"assistant","content":response.choices[0].message.content}
        )
        # 返回AI的回复
        return response.choices[0].message.content 

    def clear(self):
        self.__load_template__(self.system_prompt)
        self.create_prompt_template()