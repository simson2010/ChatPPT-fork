import gradio as gr
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

# 设置您的OpenAI API密钥
api_key = ""

chat = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=api_key)


def chat_with_llm(message, history):
    # 将历史对话和新消息转换为Langchain消息格式
    messages = [SystemMessage(content="你是一个有帮助的助手。")]
    for human, ai in history:
        messages.append(HumanMessage(content=human))
        messages.append(AIMessage(content=ai))
    messages.append(HumanMessage(content=message))

    # 使用Langchain进行对话
    response = chat(messages)

    # 返回AI的回复
    return response.content

# 创建Gradio界面
with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    clear = gr.Button("清除对话")

    def user(user_message, history):
        return "", history + [[user_message, None]]

    def bot(history):
        user_message = history[-1][0]
        bot_message = chat_with_llm(user_message, history[:-1])
        history[-1][1] = bot_message
        return history

    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear.click(lambda: None, None, chatbot, queue=False)

demo.launch()