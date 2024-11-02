from pathlib import Path
from openai import OpenAI
import os
from file_upload import ImageUploader
import requests
import json
from logger import LOG 

test_file = 'c:\\Users\\EricXZPan\\Pictures\\fake_body_shape-001.jpg'

upload_api_path = 'https://api.coze.cn/v1/files/upload'
chat_url = f'https://api.coze.cn/v3/chat'

bot_id = '7432590023784284197'
user_id = '213'

def send_image_and_text_to_coze(image_file, user_message = '描述图片'):

    coze_token = os.environ.get('coze_token','')
    uploader = ImageUploader(api_url=upload_api_path, token=coze_token)
    image_id = uploader.upload_image(image_file)
    if image_id == -1:
        LOG.debug(f"Upload failed plesae check above info.")
        return "图片分析失败，请重新上传"
    LOG.debug(f'[image upload][image_id]: {image_id}')

    
    headers = {
        'Authorization': f'Bearer {coze_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "bot_id": bot_id,
        "user_id": user_id,
        "stream": True,
        "auto_save_history": True,
        "meta_data":{
            "uuid":f"uuid{user_id}"
        },
        "additional_messages": [
            {
                "role": "user",
                "type": "question",
                "content": f'[{{"type":"text","text":"{user_message}"}}, {{"type":"image","file_id":"{image_id}"}}]',
                "content_type": "object_string"
            }
        ]
    }
    LOG.debug(f'send_image_and_text_to_coze:{data}')
    response = requests.post(chat_url, headers=headers, json=data)  # Send the POST request
    LOG.debug(f'chat_with_image_online: {response}')
    result = b''
    for event in response:
        result += event 
        # LOG.debug(f'working: {type(event)}')
        # LOG.debug(f'{event}')
    # LOG.debug(f'Final: {result.decode("utf-8")}')
    content = process_conversation_data(result.decode("utf-8"))
    LOG.debug(f'Final Content: {content}')
    return content  # Return the JSON response

# Example usage
# response = send_image_and_text_to_coze('7374752000116113452', '737946218936519****', '123456789', 'https://lf-bot-studio-plugin-resource.coze.cn/obj/bot-studio-platform-plugin-tos/artist/image/4ca71a5f55d54efc95ed9c06e019ff4b.png', '帮我看看这张图片里都有什么')
def process_conversation_data(conversation_data):
    contents = []
    d = conversation_data.split("event:conversation.message.completed")
    
    for event in d :
        event = event.lstrip('\n')    
        if event.startswith("data:"):
            # Extract the JSON part of the event
            json_data = event[5:]  # Remove the "data:" prefix
            # Convert the JSON string to a dictionary
            try:
                data_dict = json.loads(json_data)
            except:
                continue
            # LOG.debug(f'dict created: {data_dict}')
            # Check if 'content' is in the data and append it to the list
            if 'type' in data_dict and data_dict['type'] == 'answer' and 'content' in data_dict:
                contents.append(data_dict['content'])
    # Merge all contents into a single string
    merged_content = ' '.join(contents)
    return merged_content


# file_id = uploader.upload_image(test_file)
# bot_id = '7432590023784284197'
# image_desc = send_image_and_text_to_coze('',bot_id=bot_id, user_id='123', image_id= file_id, user_message='描述图片中有什么内容')
# LOG.debug(f'image desc: {image_desc}')

# conversation_id = '7432628144068296713'
# conversations = retrieve_conversation(conversation_id=conversation_id)
# print(conversations)