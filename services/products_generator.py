from yandex_cloud_ml_sdk import YCloudML
from yandex_cloud_ml_sdk.auth import APIKeyAuth
from dotenv import load_dotenv
import random
import os

load_dotenv('/var/www/Market_Competition/.env')

PRODUCTS_BASE = ["Сноуборд", "Велосипед", "Солнечные очки", "Зонт и дождевик", "Новогодние украшения", "Школьные принадлежности", "Пуховик", "Гамаки и шезлонги", "Термос", "Семена и рассада"]

class ProductsGenerator:
    def __init__(self):
        """Инициализация генератора"""
        self.products_inited = False
        self.products = PRODUCTS_BASE.copy()
        self.api_key = os.getenv('YANDEX_CLOUD_API_KEY')
        self.folder_id = os.getenv('YANDEX_CLOUD_FOLDER_ID')

    def init_products_list(self):
        """Инициализация списка товаров через Yandex Cloud ML"""
        if self.products_inited:
            return
        
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
        
        try:
            sdk = YCloudML(
                folder_id=self.folder_id,
                auth=APIKeyAuth(self.api_key),
            )

            result = (
                sdk.models.completions("yandexgpt")
                .configure(temperature=0.7)
                .run(messages)
            )

            for alternative in result:
                try:
                    new_products = eval(alternative.text)
                    if isinstance(new_products, list) and len(new_products) > 0:
                        self.products = new_products
                        self.products_inited = True
                        print("Список товаров успешно загружен")
                except:
                    print("Ошибка при обработке ответа от API, используется резервный список")
                break
                
        except Exception as e:
            print(f"Ошибка при загрузке списка товаров: {e}")
        
        self.products_inited = True

    def get_random_product(self):
        if not self.products_inited:
            self.init_products_list()
        return random.choice(self.products)

product_generator = ProductsGenerator()
