import os
import asyncio
from yandex_cloud_ml_sdk import YCloudML
from yandex_cloud_ml_sdk.auth import APIKeyAuth
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv('/var/www/Market_Competition/.env')

async def test_api():
    print("Инициализация API...")
    
    try:
        sdk = YCloudML(
            folder_id=os.getenv('YANDEX_CLOUD_FOLDER_ID'),
            auth=APIKeyAuth(os.getenv('YANDEX_CLOUD_API_KEY'))
        )

        print("Отправка запроса к API...")
        
        # Правильный формат запроса
        result = await sdk.models.completions("yandexgpt").configure(
            temperature=0.7
        ).run([
            {
                "role": "system",
                "text": "Ты должен вернуть только Python-список в формате [\"товар1\", \"товар2\"]"
            },
            {
                "role": "user", 
                "text": "Сгенерируй список из 10 товаров для интернет-магазина, популярных зимой."
            }
        ])

        print("\nОтвет API:")
        for alternative in result.alternatives:
            print(f"Статус: {alternative.status}")
            print(f"Текст: {alternative.text}")
            
            try:
                # Безопасное преобразование ответа
                products = eval(alternative.text)
                if isinstance(products, list):
                    print("\nУспешно получен список товаров:")
                    for product in products:
                        print(f"- {product}")
                else:
                    print("Ответ не является списком")
            except:
                print("Не удалось преобразовать ответ в список")

    except Exception as e:
        print(f"\nОшибка API: {str(e)}")

asyncio.run(test_api())
