import requests
import os
from logger import LOG

API_URL = "https://api-inference.huggingface.co/models/openai/whisper-small"

hf_token = ""

def query(filename):
    LOG.info(f'ready to query : {filename}')
    global hf_token
    if hf_token == "":
        hf_token = os.getenv("HF_TOKEN")

    headers = {"Authorization": f"Bearer {hf_token}"}

    with open(filename, "rb") as f:
        data = f.read()
    response = requests.post(API_URL, headers=headers, data=data)
    return response.json()

# output = query("sample1.flac")

def asr(audio_file, task="transcribe"):
    """
    对音频文件进行语音识别或翻译。

    参数:
    - audio_file: 输入的音频文件路径
    - task: 任务类型（"transcribe" 表示转录，"translate" 表示翻译）

    返回:
    - text: 识别或翻译后的文本内容
    """
    LOG.debug(f"file :{audio_file}")
    text = query(audio_file)

    return text["text"] if "text" in text else ""

def transcribe(inputs, task):
    
    LOG.debug(f"inputs: {inputs}")
    # 检查是否提供了音频文件
    if not inputs or not os.path.exists(inputs):
        raise gr.Error("未提交音频文件！请在提交请求前上传或录制音频文件。")
    
    # 检查音频文件格式
    file_ext = os.path.splitext(inputs)[1].lower()
    if file_ext not in ['.wav', '.flac', '.mp3']:
        LOG.error(f"文件格式错误：{inputs}")
        raise gr.Error("不支持的文件格式！请上传 WAV、FLAC 或 MP3 文件。")
    
    return asr(inputs, task)

if __name__ == "__main__": 
    import gradio as gr
    # 定义麦克风输入的接口实例，可供外部模块调用
    mf_transcribe = gr.Interface(
        fn=transcribe,  # 执行转录的函数
        inputs=[
            gr.Audio(sources="microphone", type="filepath", label="麦克风输入"),  # 使用麦克风录制的音频输入
            gr.Radio(["transcribe", "translate"], label="任务类型", value="transcribe"),  # 任务选择（转录或翻译）
        ],
        outputs="text",  # 输出为文本
        title="Whisper Large V3: 语音识别",  # 接口标题
        description="使用麦克风录制音频并进行语音识别或翻译。",  # 接口描述
        flagging_mode="never",  # 禁用标记功能
    )

    # 定义文件上传的接口实例，用于处理上传的音频文件
    file_transcribe = gr.Interface(
        fn=transcribe,  # 执行转录的函数
        inputs=[
            gr.Audio(sources="upload", type="filepath", label="上传音频文件"),  # 上传的音频文件输入
            gr.Radio(["transcribe", "translate"], label="任务类型", value="transcribe"),  # 任务选择（转录或翻译）
        ],
        outputs="text",  # 输出为文本
        title="Whisper Large V3: 转录音频文件",  # 接口标题
        description="上传音频文件（WAV、FLAC 或 MP3）并进行语音识别或翻译。",  # 接口描述
        flagging_mode="never",  # 禁用标记功能
    )
    # 创建一个 Gradio Blocks 实例，用于包含多个接口
    with gr.Blocks() as demo:
        # 使用 TabbedInterface 将 mf_transcribe 和 file_transcribe 接口分别放置在 "麦克风" 和 "音频文件" 选项卡中
        gr.TabbedInterface(
            [mf_transcribe, file_transcribe],
            ["麦克风", "音频文件"]
        )

    # 启动Gradio应用，允许队列功能，并通过 HTTPS 访问
    demo.queue().launch(
        share=False,
        server_name="0.0.0.0",
        # auth=("django", "1234") # ⚠️注意：记住修改密码
    )
