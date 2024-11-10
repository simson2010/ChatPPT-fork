## reflection_chatbot.py

from abc import ABC, abstractmethod

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder  # 导入提示模板相关类
from langchain_core.messages import HumanMessage  # 导入消息类
from langchain_core.runnables.history import RunnableWithMessageHistory  # 导入带有消息历史的可运行类

from logger import LOG  # 导入日志工具
from chat_history import get_session_history
from create_graph import create_builder, run_graph

import os
xai_key = os.getenv('XAI_API_KEY')  # 从环境变量获取 XAI API 密钥
if xai_key is None:
    raise ValueError("XAI API key not found in environment variables.")


class ChatBot(ABC):
    """
    聊天机器人基类，提供聊天功能。
    """
    def __init__(self, prompt_file="./prompts/chatbot.txt", session_id=None):
        self.prompt_file = prompt_file
        self.reflect_prompt_file = './prompts/reflection_prompt.txt'
        self.session_id = session_id if session_id else "default_session_id"
        self.prompt = self.load_prompt()
        self.reflect_prompt = self.load_reflect_prompt()
        # LOG.debug(f"[ChatBot Prompt]{self.prompt}")
        self.create_chatbot()

    def load_prompt(self):
        """
        从文件加载系统提示语。
        """
        try:
            with open(self.prompt_file, "r", encoding="utf-8") as file:
                return file.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到提示文件 {self.prompt_file}!")

    def load_reflect_prompt(self):  
        try:
            with open(self.reflect_prompt_file, "r", encoding="utf-8") as file:
                return file.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到提示文件 {self.prompt_file}!")

    def create_chatbot(self):
        """
        初始化聊天机器人，包括系统提示和消息历史记录。
        """
        # 创建聊天提示模板，包括系统提示和消息占位符
        system_prompt = ChatPromptTemplate.from_messages([
            ("system", self.prompt),  # 系统提示部分
            MessagesPlaceholder(variable_name="messages"),  # 消息占位符
        ])

        # 初始化 ChatOllama 模型，配置参数
        self.chatbot = system_prompt | ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=4096
        )

        # 将聊天机器人与消息历史记录关联
        self.chatbot_with_history = RunnableWithMessageHistory(self.chatbot, get_session_history)            

        reflection_prompt = ChatPromptTemplate.from_messages([
            ("system", self.reflect_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ])

        # llm_reflection = ChatOpenAI(model="gpt-4o-mini", max_tokens=8192, temperature = 0)
        llm_reflection = ChatOpenAI(api_key=xai_key,model="grok-beta", max_tokens=4096, temperature=0, base_url="https://api.x.ai/v1")
        self.reflect = reflection_prompt | llm_reflection

        self.builder = create_builder(self.chatbot_with_history, self.reflect)
    
    async def chat_with_history(self, user_input, session_id=None):
        """
        处理用户输入，生成包含聊天历史的回复。

        参数:
            user_input (str): 用户输入的消息
            session_id (str, optional): 会话的唯一标识符

        返回:
            str: AI 生成的回复
        """
        if session_id is None:
            session_id = self.session_id
    
        ###output format [('writer', 'content')]
        response = await run_graph(self.builder, user_input, session_id)

        LOG.debug(f"[ChatBot] {response}")  # 记录调试日志

        pptContent = [m for m in response if m[0] == 'writer'][-1][1]
        if pptContent[0]=="#" :
            LOG.debug(pptContent)
            return pptContent
        else:
            startIndex = pptContent.index("#")
            LOG.debug(pptContent[startIndex:])
            return pptContent[startIndex:]
