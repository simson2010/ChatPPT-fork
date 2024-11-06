import os
from zhipuai import ZhipuAI
from logger import LOG

# 从环境变量获取 API key
api_key = os.getenv("ZHIPUAI_API_KEY")
if not api_key:
    raise ValueError("请设置环境变量 ZHIPUAI_API_KEY")
client = ZhipuAI(api_key=api_key)
  
default_model = 'cogview-3-plus'
def generate_image_zhipu(prompt): 

    try:
        response = client.images.generations(
            model=default_model, #填写需要调用的模型编码
            prompt=f"{prompt}，科学配图， 风络：摄影",
        )
        LOG.info(response.data[0].url)
        return response.data[0].url
    except Exception as err:
        LOG.info(err)
    
# import requests

# API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
# headers = {"Authorization": "Bearer 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"}

# def query(payload):
# 	response = requests.post(API_URL, headers=headers, json=payload)
# 	return response.content

# image_bytes = query({
# 	"inputs": "real world, Earth movment",
# })

# # You can access the image with PIL.Image for example
# import io
# from PIL import Image
# image = Image.open(io.BytesIO(image_bytes))
# image.save("./aaa.png")