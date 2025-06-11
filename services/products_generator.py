from yandex_cloud_ml_sdk import YCloudML
from yandex_cloud_ml_sdk.auth import APIKeyAuth
from dotenv import load_dotenv
import os
import random
import re
import ast

load_dotenv('/var/www/Market_Competition/.env')

PRODUCTS_BASE = [
    "Сноуборд", "Велосипед", "Солнечные очки", "Зонт и дождевик",
    "Новогодние украшения", "Школьные принадлежности", "Пуховик",
    "Гамаки и шезлонги", "Термос", "Семена и рассада"
]

class ProductsGenerator:
    def __init__(self):
        self.products_inited = False
        self.products = PRODUCTS_BASE.copy()
        self.api_key = os.getenv('YANDEX_CLOUD_API_KEY')
        self.folder_id = os.getenv('YANDEX_CLOUD_FOLDER_ID')

    def _clean_api_response(self, text):
        """Очищает ответ API от лишних символов"""
        return re.sub(r'^```(python)?|```$', '', text, flags=re.MULTILINE).strip()

    def init_products_list(self):
        """Инициализация списка товаров через Yandex Cloud ML"""
        if self.products_inited or not all([self.api_key, self.folder_id]):
            return

        try:
            sdk = YCloudML(
                folder_id=self.folder_id,
                auth=APIKeyAuth(self.api_key)
            )

            result = sdk.models.completions("yandexgpt").configure(
                temperature=0.7
            ).run([
                {
                    "role": "system",
                    "text": "Верни только Python-список в формате [\"товар1\", \"товар2\"]. Без Markdown."
                },
                {
                    "role": "user",
                    "text": "Сгенерируй список из 24 товаров для интернет-магазина, популярных в разные сезоны."
                }
            ])

            if result.alternatives:
                cleaned = self._clean_api_response(result.alternatives[0].text)
                self.products = ast.literal_eval(cleaned)
                self.products_inited = True

        except Exception as e:
            print(f"Ошибка генерации: {e}")

    def get_random_product(self):
        """Возвращает случайный товар"""
        if not self.products_inited:
            self.init_products_list()
        return random.choice(self.products)

product_generator = ProductsGenerator()
