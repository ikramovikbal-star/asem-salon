ACEM — ГОТОВЫЙ САЙТ С БАЗОЙ ДАННЫХ
===================================

В проекте уже есть:
- frontend: public/index.html
- backend: Flask (app.py)
- база: PostgreSQL
- локальный fallback: SQLite
- админка через серверную сессию
- защита от двойной записи на одинаковое время
- WhatsApp после успешной записи

1. ДОБАВЬТЕ СВОИ КАРТИНКИ
-------------------------
Положите эти файлы в папку public:

ChatGPT Image 25 авг. 2026 г., 15_51_43.png
Gemini_Generated_Image_w4wfijw4wfijw4wf.jpg
Gemini_Generated_Image_9i35ji9i35ji9i35.jpg
Gemini_Generated_Image_721nsj721nsj721n.jpg
Gemini_Generated_Image_o543deo543deo543.jpg
Gemini_Generated_Image_sf92jrsf92jrsf92.jpg

Если имена ваших файлов отличаются — поменяйте src в public/index.html.

2. БЫСТРЫЙ ЗАПУСК НА WINDOWS
----------------------------
Дважды нажмите:
RUN_WINDOWS.bat

При первом запуске будет создан файл .env.

Откройте .env и укажите:
ADMIN_PASSWORD=ваш_пароль
SECRET_KEY=любая_длинная_случайная_строка

DATABASE_URL можно пока оставить пустым.
Тогда сайт будет использовать SQLite локально.

После запуска откройте:
http://127.0.0.1:5000

3. POSTGRESQL
-------------
Для настоящего сервера создайте PostgreSQL базу и вставьте строку подключения:

DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DATABASE

После запуска Flask сам создаст таблицу bookings.

Файл schema.sql приложен только для ручного создания таблицы, если понадобится.

4. RENDER
---------
Загрузите папку проекта в GitHub.

На Render:
- создайте Web Service
- Build Command:
  pip install -r requirements.txt
- Start Command:
  gunicorn app:app

Добавьте Environment Variables:
ADMIN_PASSWORD=ваш_пароль
SECRET_KEY=длинная_случайная_строка
DATABASE_URL=ваша_postgresql_строка

Также приложен render.yaml.

5. КАК ТЕПЕРЬ РАБОТАЕТ ЗАПИСЬ
-----------------------------
Клиент выбирает:
услугу -> дату -> время -> имя -> телефон

Браузер отправляет данные на:
POST /api/bookings

Flask сохраняет запись в PostgreSQL.

Свободное/занятое время берётся из:
GET /api/booked-times

Админка получает записи из:
GET /api/admin/bookings

Удаление:
DELETE /api/admin/bookings/<id>

6. ВАЖНО
--------
Никогда не вставляйте ADMIN_PASSWORD или DATABASE_URL в index.html.

Файл .env уже добавлен в .gitignore, поэтому его не нужно загружать на GitHub.
