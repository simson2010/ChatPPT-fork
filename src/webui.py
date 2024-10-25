import gradio as gr
import os
from input_parser import parse_input_text
from template_manager import load_template, get_layout_mapping, print_layouts
from ppt_generator import generate_presentation
from LLMChat import LLMChat
from layout_manager import LayoutManager
from config import Config
from logger import LOG

config = Config()  # 加载配置文件
systemPrompt_path = os.path.join(os.getcwd(), "prompts", "formatter.txt")  # Combine with the current working directory

chat = LLMChat(model_name = config.model_name, system_prompt=systemPrompt_path)

ppt_content = "" 
prs =  load_template(config.ppt_template)  # 加载模板文件
LOG.info("可用的幻灯片布局:")  # 记录信息日志，打印可用布局
layout_manager = LayoutManager(config.layout_mapping)


def chat_with_llm(message, history):
    global ppt_content
    # 使用Langchain进行对话
    response = chat.chat_with_llm(message, history)
    # 默认LLM返回的使用PPT内容
    ppt_content = response
    # 返回AI的回复
    return response

def createPPT():
    LOG.info("Creating PPT")
    LOG.info(f"PPT Content:\n{ppt_content}")
    powerpoint_data, presentation_title = parse_input_text(ppt_content, layout_manager)
    # 定义输出 PowerPoint 文件的路径
    output_pptx = f"outputs/temp.pptx"
    
    # 调用 generate_presentation 函数生成 PowerPoint 演示文稿
    path = generate_presentation(powerpoint_data, config.ppt_template, output_pptx)
    full_path = os.path.join(os.getcwd(), path).replace("/","\\")
    LOG.debug(full_path.replace("/","\\")) 
    return gr.DownloadButton("Download",value=full_path, visible=True)

def clearHistory():
    chat.clear()
    return  [(None, None)], gr.DownloadButton("Download",visible=False)

# 创建Gradio界面
with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    download_button = gr.DownloadButton("create ppt", value="sample", visible=False)
    create_button = gr.Button("创建PPT")
    clear = gr.Button("清除对话")

    def user(user_message, history):
        download_button.visible = False
        return "", history + [[user_message, None]],  gr.DownloadButton("Download",visible=False)

    def bot(history):
        user_message = history[-1][0]
        bot_message = chat_with_llm(user_message, history[:-1])
        history[-1][1] = bot_message
        return history

    msg.submit(user, [msg, chatbot], [msg, chatbot, download_button], queue=False).then(
        bot, chatbot, chatbot
    )
    clear.click(clearHistory, None, [chatbot, download_button], queue=False)

    create_button.click(createPPT, None, download_button)

demo.launch() 