import os
from yandex_cloud_ml_sdk import YCloudML
from yandex_cloud_ml_sdk.auth import APIKeyAuth
from dotenv import load_dotenv
import ast

# Загрузка переменных окружения
load_dotenv('/var/www/Market_Competition/.env')

def test_api():
    print("Инициализация API...")
    
    try:
        # Инициализация SDK
        sdk = YCloudML(
            folder_id=os.getenv('YANDEX_CLOUD_FOLDER_ID'),
            auth=APIKeyAuth(os.getenv('YANDEX_CLOUD_API_KEY'))
        )

        print("Отправка запроса к API...")
        
        # Правильный синхронный запрос
        result = sdk.models.completions("yandexgpt").configure(
            temperature=0.7
        ).run([
            {
                "role": "system",
                "text": "Ты должен вернуть только Python-список в формате [\"товар1\", \"товар2\"]"
            },
            {
                "role": "user", 
                "text": "Сгенерируй список из 10 популярных товаров для интернет-магазина. Только список, без пояснений."
            }
        ])

        print("\nОтвет API получен. Статус:", result.alternatives[0].status)
        
        # Обработка ответа
        if result.alternatives:
            response_text = result.alternatives[0].text
            print("Сырой ответ:", response_text)
            
            try:
                # Безопасное преобразование
                products = ast.literal_eval(response_text.strip())
                if isinstance(products, list):
                    print("\nУспешно получен список товаров:")
                    for i, product in enumerate(products, 1):
                        print(f"{i}. {product}")
                else:
                    print("Ошибка: ответ не является списком")
            except (SyntaxError, ValueError) as e:
                print(f"Ошибка парсинга: {e}\nПолный ответ:")
                print(response_text)

    except Exception as e:
        print(f"\nОшибка API: {str(e)}")

if __name__ == "__main__":
    test_api()
