<div align="center">
  <h1>Информационный бот</h1>
  <p>
    <strong>Мультифункциональный бот</strong>
  </p>
  <p>

[![](https://img.shields.io/badge/Telegram-bot-blue?logo=telegram)](https://t.me/tost_game_bot?start=start)
[![](https://img.shields.io/badge/A_rest-db_server-blue)](https://qwertedrtvghjn.pythonanywhere.com)

  </p>
</div>

<!-- shields.io for this icons (да это я сделал) -->
Разработка бота для Telegram, выполняющего вспомогательные и информационные функции.

## Цели проекта:
- создание асинхронного бота
- реализация задуманных способностей бота
- реализация функций отслеживания действий в базу данных для отображения статистики в боте

## Задуманные способности бота:
### Получение различной информации
- Текущий курс валют
- узнать местоположение по айпи
- чат гпт
- погода
- поиск картинок по запросу

### Помощник по чату
- Бан/мут/предупреждение пользователя
- спам детект
- фильтр слов
- статистика чата/пользователя

### Работа с файлами на пространстве, где был запущен бот
- терминал через сообщение
- скинуть файл
- загрузить файл
- выгрузка/загрузка файлов с/на сервера


Начало разработки - 25.03.24


Конец разработки - дата защиты проекта


- Реализация 1 пункта - 26 - 31 марта
- Реализация 2 пункта 1 - 7 апреля
- Реализация 3 пункта 8.04 - дата защиты-2 дня
- Подготовка презентации - дата защиты-2 дня - дата защиты

### Обозначения в коммитах


~folder - папка была немного отредактированна, фиксы багов/исправления


+bot/REST - добавление каких либо функций в бота/рест сервер


-file/folder - удаление файла/папки


|-file/folder - релокация файла/папки


## Установка

Нужен Python 3.11

<br>

Клонирование репозитория
~~~
git clone https://github.com/ma3rd-nepon/Telegram-bot.git
~~~

<br>

Установка зависимостей
~~~
pip install -r requirements.txt
~~~
или
~~~
python -m pip install -r requirements.txt
~~~

<br>

Запуск бота
~~~
python main.py
~~~

Запуск сайта с базой данных (запускать на сервере)
~~~
python app.py
~~~


### Почему pyrogram

Библиотека Pyrogram использует не традиционные HTTP Bot API. Сообщество написало свой вариант работы ботов на основе MTProto 


[Различия MTProto и HTTP Bot API](https://github.com/LonamiWebs/Telethon/wiki/MTProto-vs-HTTP-Bot-API)


[MTProto vs HTTP Bot API](https://docs.telethon.dev/en/stable/concepts/botapi-vs-mtproto.html)

<div>
  <img src="https://docs.pyrogram.org/_static/img/mtproto-vs-bot-api.png">
</div>



<!-- ## Ссылки
### [Рест сервер](https://qwertedrtvghjn.pythonanywhere.com)

### [Телеграм-Бот](https://t.me/tost_game_bot?start=start)
-->

