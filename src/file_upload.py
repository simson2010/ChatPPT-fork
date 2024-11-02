# src/file_upload.py

import requests
from logger import LOG

class ImageUploader:
    def __init__(self, api_url, token):
        self.api_url = api_url
        self.token = token

    def upload_image(self, file_path):
        headers = {
            'Authorization': f'Bearer {self.token}',
        }
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(self.api_url, headers=headers, files=files)
            return self.handle_response_json(response.json())  # Return the response as JSON

    def upload_image_from_browser(self, file):
        LOG.debug(f'[upload_image_from_browser][file:] {file}')
        headers = {
            'Authorization': f'Bearer {self.token}',
        }
        files = {'file': file}
        response = requests.post(self.api_url, headers=headers, files=files)
        return self.handle_response_json(response.json())

    def handle_response_json(self, resJson):
        if resJson and resJson['code'] == 0:
            LOG.debug(f'uploaded file id is : {resJson["data"]["id"]}, name: {resJson["data"]["file_name"]}, {resJson["data"]["bytes"]}')
            return resJson['data']['id']
        else: 
            LOG.debug(f'[upload failed]{resJson["code"]} | {resJson["msg"]}')
            return -1

# Example usage:
# uploader = ImageUploader('https://api.coze.cn/v1/files/upload', 'pat_OYDacMzM3WyOWV3Dtj2bHRMymzxP****')
# result = uploader.upload_image('/test/1120.jpeg')
# print(result)