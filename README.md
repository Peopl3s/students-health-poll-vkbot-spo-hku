# ВКонтакте бот для опроса о состоянии здоровья студентов университета 

После запуска бот отправаляет в личные сообщения вопросы о состоянии здоровья всем студентам из txt-файла. Результаты опроса записывает в Google Таблицу (Google Sheets). Сообщения об ошибках логирует в файл.

### 👨‍💻 Технологии
  - :heavy_check_mark: Python3 :heavy_check_mark: Aiogram :heavy_check_mark: Google Sheet API

### 👾 Запуск
```bash
python -m pip install -r requirements.txt
python bot.py
```
Старт опроса: ```!start <название_файла_со_списком_id> <ссылка_на_google_таблицу>``` (предвариательно студенты должны "Разрешать сообщения" от публичной страницы бота. 


### 🖌️ Пример работы
![alt text](https://github.com/Peopl3s/students-health-poll-vkbot-spo-hku/blob/main/screens/poll1.PNG)


![alt text](https://github.com/Peopl3s/students-health-poll-vkbot-spo-hku/blob/main/screens/poll2.PNG)


![alt text](https://github.com/Peopl3s/students-health-poll-vkbot-spo-hku/blob/main/screens/poll3.PNG)


![alt text](https://github.com/Peopl3s/students-health-poll-vkbot-spo-hku/blob/main/screens/table.PNG)


