import os
from dotenv import load_dotenv
load_dotenv()

from yandex_cloud_ml_sdk import YCloudML
from yandex_cloud_ml_sdk.auth import APIKeyAuth

print("Тестирование API...")
sdk = YCloudML(
    folder_id=os.getenv('FOLDER_ID'),
    auth=APIKeyAuth(os.getenv('YANDEX_API_KEY'))
)
response = sdk.models.completions("yandexgpt").run([{"role": "user", "text": "Тестовый запрос"}])
print(response)
