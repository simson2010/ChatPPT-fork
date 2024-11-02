import gradio as gr
import os
from logger import LOG


def common_chat(message, history):
    LOG.debug(f"common:{message}")
    return message

with gr.Blocks(
    title="ChatPPT",
    css="""
    body { animation: fadeIn 2s; }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    """
) as demo:
    # 创建聊天机器人界面，提示用户输入
    contents_chatbot = gr.Chatbot(
        placeholder="<strong>AI 一键生成 PPT</strong><br><br>输入你的主题内容或上传音频文件",
        height=500,
        type="messages",
    )

    gr.ChatInterface(
        fn=common_chat,  # 处理用户输入的函数
        chatbot=contents_chatbot,  # 绑定的聊天机器人
        type="messages",
        title="hello world",
        # multimodal=True  # 支持多模态输入（文本和文件）
    )

demo.launch(share=True)