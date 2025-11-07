# 🚀 Инструкция по развертыванию Lunch Bot

Бот сейчас работает локально на вашем компьютере. Чтобы он работал 24/7, нужен хостинг.

## ⭐ Вариант 1: Railway.app (РЕКОМЕНДУЕТСЯ - бесплатно и просто)

### Шаг 1: Подготовка
1. Создайте аккаунт на [railway.app](https://railway.app/)
2. Установите Git на компьютер (если еще нет)
3. Создайте репозиторий на GitHub

### Шаг 2: Загрузка кода на GitHub
```bash
cd /Users/sevak.martirosyan/lunch_bot

# Инициализируем git
git init

# Добавляем все файлы
git add .

# Делаем коммит
git commit -m "Initial commit - Lunch Bot"

# Создайте репозиторий на github.com, затем:
git remote add origin https://github.com/ВАШ_USERNAME/lunch_bot.git
git branch -M main
git push -u origin main
```

### Шаг 3: Деплой на Railway
1. Зайдите на [railway.app](https://railway.app/)
2. Нажмите **"New Project"**
3. Выберите **"Deploy from GitHub repo"**
4. Выберите ваш репозиторий `lunch_bot`
5. Railway автоматически определит Python проект

### Шаг 4: Настройка переменных окружения
В панели Railway:
1. Перейдите в раздел **"Variables"**
2. Добавьте переменные из вашего `.env` файла:
   - `BOT_TOKEN` = ваш токен от BotFather
   - `ADMIN_ID` = ваш Telegram ID
   - `DATABASE_NAME` = lunch_bot.db

### Шаг 5: Запуск
Railway автоматически запустит бота!

---

## 🐍 Вариант 2: PythonAnywhere (бесплатно)

### Шаг 1: Регистрация
1. Создайте аккаунт на [pythonanywhere.com](https://www.pythonanywhere.com/)
2. Выберите бесплатный план

### Шаг 2: Загрузка кода
1. В PythonAnywhere откройте **"Files"**
2. Загрузите все файлы проекта или клонируйте из GitHub:
```bash
git clone https://github.com/ВАШ_USERNAME/lunch_bot.git
cd lunch_bot
```

### Шаг 3: Установка зависимостей
Откройте Bash консоль:
```bash
cd lunch_bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Шаг 4: Создайте .env файл
```bash
nano .env
```
Добавьте ваши настройки.

### Шаг 5: Запуск бота
1. Перейдите в **"Tasks"**
2. Добавьте задачу:
   - Command: `/home/ВАШ_USERNAME/lunch_bot/venv/bin/python /home/ВАШ_USERNAME/lunch_bot/main.py`
   - Schedule: `daily at 00:00`

Или запустите в консоли:
```bash
python main.py
```

---

## 🖥️ Вариант 3: VPS Сервер (DigitalOcean, AWS, и др.)

### Требования:
- Ubuntu 20.04+
- Python 3.12+
- systemd для автозапуска

### Шаг 1: Подключение к серверу
```bash
ssh root@ВАШ_IP
```

### Шаг 2: Установка Python и зависимостей
```bash
apt update
apt install python3.12 python3.12-venv git -y
```

### Шаг 3: Клонирование проекта
```bash
cd /opt
git clone https://github.com/ВАШ_USERNAME/lunch_bot.git
cd lunch_bot
```

### Шаг 4: Настройка окружения
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Шаг 5: Создание .env файла
```bash
nano .env
```

### Шаг 6: Создание systemd сервиса
```bash
nano /etc/systemd/system/lunch_bot.service
```

Содержимое:
```ini
[Unit]
Description=Lunch Bot Telegram
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/lunch_bot
Environment="PATH=/opt/lunch_bot/venv/bin"
ExecStart=/opt/lunch_bot/venv/bin/python /opt/lunch_bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Шаг 7: Запуск сервиса
```bash
systemctl daemon-reload
systemctl enable lunch_bot
systemctl start lunch_bot

# Проверка статуса
systemctl status lunch_bot

# Просмотр логов
journalctl -u lunch_bot -f
```

---

## 📊 Сравнение вариантов

| Платформа | Цена | Сложность | Время работы |
|-----------|------|-----------|--------------|
| Railway | Бесплатно (500ч/мес) | Легко ⭐⭐⭐ | 24/7 |
| PythonAnywhere | Бесплатно | Средне ⭐⭐ | 24/7 |
| VPS | От $5/мес | Сложно ⭐ | 24/7 |

---

## ✅ Проверка работы

После деплоя:
1. Откройте Telegram
2. Напишите боту `/start`
3. Проверьте команду `/lunch`

## 🔧 Обновление бота

### На Railway/GitHub:
```bash
git add .
git commit -m "Update bot"
git push
```
Railway автоматически обновит бота.

### На VPS:
```bash
cd /opt/lunch_bot
git pull
systemctl restart lunch_bot
```

---

## 🆘 Поддержка

Если возникли проблемы:
1. Проверьте логи
2. Убедитесь, что все переменные окружения установлены
3. Проверьте, что токен бота правильный

**Рекомендую начать с Railway - это самый простой вариант!** 🚀

