#!/usr/bin/env python3

from __future__ import annotations
from yandex_cloud_ml_sdk import YCloudML
from yandex_cloud_ml_sdk.auth import APIKeyAuth
from dotenv import load_dotenv
import random
import os

load_dotenv('/var/www/Market_Competition/.env')

messages = [
    {
        "role": "system",
        "text": "Сгенерируй список из 24 товаров. Верни только список в формате [\"товар1\", \"товар2\", ...], без кавычек вокруг и без пояснений.",
    },
    {
        "role": "user",
        "text": """Создай список товаров для продажи в интернет-магазине, которые популярны в разные сезоны года. 
Зимой - зимние виды спорта, новогодние товары, теплая одежда. 
Весной - садовый инвентарь, весенняя одежда, товары для уборки. 
Летом - пляжные принадлежности, летний спорт, охлаждающие товары. 
Осенью - школьные товары, осенняя одежда, товары для дома. 
Верни только Python список в указанном формате.""",
    },
]

def main():
    try:
        sdk = YCloudML(
            folder_id=os.getenv('YANDEX_CLOUD_FOLDER_ID'),
            auth=APIKeyAuth(os.getenv('YANDEX_CLOUD_API_KEY')),
        )

        result = (
            sdk.models.completions("yandexgpt")
            .configure(temperature=0.7)
            .run(messages)
        )

        for alternative in result:
            print(alternative.text)
            
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    main()
