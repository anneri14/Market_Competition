## Многопользовательская экономическая игра “Market Competition”

[Cсылка на игру](http://market-competition.ru)

## Содержание

- [Описание](#описание)
- [Установка и запуск игры локально](#установка-и-запуск-игры)
- [Стек технологий](#стек-технологий)
- [Структура проекта](#структура-проекта)
- [Контакты](#контакты)


## Описание

### Количество игроков:
В игре принимают участие 2 продавца (люди) и 1 покупатель (компьютер). 

### Цель: 
В ходе игры выигрывает тот игрок, который смог лучше прорекламировать свой бренд (к кому пришло больше покупателей), чем его противник. 

### Продолжительность: 
Игра состоит из серии быстрых раундов, что делает ее динамичной, каждый из которых длится 30 секунд. Всего в игре предусмотрено 16 раундов. 

### Правила игры:
Продавцы независимо друг от друга устанавливают минимальную цену и качество своих товаров/услуг в зависимости от времени года, помимо этого продавец опционально может вложиться в рекламу своего бренда. Каждому продавцу в начале игры доступно 100 ед., чтобы оплатить рекламу и качество своих товаров.  Покупатель сравнивает условия обоих продавцов и делает выбор в пользу наиболее выгодного (в соотношении цены-качества) и наиболее привлекательного продавца, при этом учитывая рекламу продавца. После этого раунд заканчивается. Продавцы видят свой бюджет и в начале нового раунда могут скорректировать свои условия. В конце игры подсчитывается успех обоих продавцов и на основе этих результатов определяется победитель - кто смог больше привлечь покупателей.


## Установка и запуск игры локально

1) Склонируйте репозиторий:
    ```bash
   git clone https://github.com/anneri14/Market_Competition.git
   cd Market_Competition
   ```
2) Настройте виртуальное окружение:
    ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3) Установите зависимости:
    ```bash
   pip install -r requirements.txt
   ```
4) Запустите приложение локально:
    ```bash
   uvicorn app:app
   ```

После запуска приложения откройте браузер и перейдите по адресу `http://127.0.0.1:8000`


## Стек технологий

### Frontend:
- HTML
- CSS
- Jinja2 Templates

### Backend:
- FastAPI
- WebSocket
- YandexGPT + Yandex Cloud API

### Design:
- Figma


### Особенности:
Интеграция с YandexGPT позволяет отправлять запросы к YandexGPT API через Yandex Cloud API. В результате автоматически генерируется список товаров и передается ввиде списка на странице player_1.html, player_2.html. 

## Структура проекта

```
market_competition/
├── static/
│   ├── css/
        ├── style_enter.css
        ├── style_landing.css
        ├── style_main.css
        ├── style_player.css
        ├── style_win_fail_pages.css
├── templates/
    ├── enter.html
    ├── landing.html
    ├── main_page.html
    ├── player_1.html
    ├── player_2.html
    ├── win_page.html
    ├── fail_page.html
    ├── draw_page.htm
├── router/
    ├── game.py
    ├── pages.py
    ├── authentication.py
├── websocket/
    ├── manager.py
├── services/
    ├── products_generator.py
├── app.py
├── requirements.txt
├── README.md
```

В папке static расположены статические файлы типа .css, отвечающие за стиль.

В папке templates расположены файлы типа .html, отвечающие за HTML-шаблоны.

В папке router расположены файлы типа .py, отвечающие за маршруты FastAPI.

В папке websocket расположен файл типа .py, отвечающий за связь между игроками в режиме реального времени.

В папке services расположен файл типа .py, отвечающие за генерацию списка товаров с помощью YandexGPT.

Файл requirements.txt - зависимости.

Файл README.md - документация.


## Контакты
По всем вопросам: 

- [Telegram](https://t.me/ann_eri)
- Почта - akerinova@edu.hse.ru



