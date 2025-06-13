import os
from yandex_cloud_ml_sdk import YCloudML
from yandex_cloud_ml_sdk.auth import APIKeyAuth
from dotenv import load_dotenv
import ast
import re

# Загрузка переменных окружения
load_dotenv('/var/www/Market_Competition/.env')

def clean_api_response(text):
    """Очищает ответ API от лишних символов"""
    # Удаляем обратные кавычки и Markdown-форматирование
    text = re.sub(r'^```(python)?|```$', '', text, flags=re.MULTILINE)
    # Удаляем лишние пробелы и переносы строк
    return text.strip()

def test_api():
    print("Инициализация API...")
    
    try:
        sdk = YCloudML(
            folder_id=os.getenv('YANDEX_CLOUD_FOLDER_ID'),
            auth=APIKeyAuth(os.getenv('YANDEX_CLOUD_API_KEY'))
        )

        print("Отправка запроса к API...")
        
        result = sdk.models.completions("yandexgpt").configure(
            temperature=0.7
        ).run([
            {
                "role": "system",
                "text": "Ты должен вернуть только Python-список в формате [\"товар1\", \"товар2\"]. Не используй Markdown и обратные кавычки."
            },
            {
                "role": "user", 
                "text": "Сгенерируй список из 10 популярных товаров для интернет-магазина. Только список, без пояснений."
            }
        ])

        print("\nОтвет API получен. Статус:", result.alternatives[0].status)
        
        if result.alternatives:
            raw_response = result.alternatives[0].text
            print("Сырой ответ:", raw_response)
            
            try:
                # Очищаем ответ перед парсингом
                cleaned_response = clean_api_response(raw_response)
                products = ast.literal_eval(cleaned_response)
                
                if isinstance(products, list):
                    print("\nУспешно получен список товаров:")
                    for i, product in enumerate(products, 1):
                        print(f"{i}. {product}")
                else:
                    print("Ошибка: ответ не является списком")
            except (SyntaxError, ValueError) as e:
                print(f"Ошибка парсинга: {e}\nОчищенный ответ:")
                print(cleaned_response)

    except Exception as e:
        print(f"\nОшибка API: {str(e)}")

if __name__ == "__main__":
    test_api()
