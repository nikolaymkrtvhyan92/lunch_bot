#!/bin/bash

clear

echo "╔════════════════════════════════════════════════════════╗"
echo "║     🍽️  ЗАПУСК БОТА - ПОШАГОВАЯ ИНСТРУКЦИЯ  🍽️       ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Проверяем .env
if [ ! -f .env ]; then
    echo "❌ ОШИБКА: Файл .env не найден!"
    echo ""
    echo "Выполните сначала:"
    echo "  cp .env.example .env"
    echo "  open -e .env"
    echo ""
    exit 1
fi

# Проверяем заполнен ли токен
if grep -q "ВСТАВЬТЕ_СЮДА_ВАШ_ТОКЕН" .env; then
    echo "❌ ОШИБКА: Токен бота не заполнен!"
    echo ""
    echo "Откройте файл .env и вставьте токен от BotFather:"
    echo "  open -e .env"
    echo ""
    echo "Замените ВСТАВЬТЕ_СЮДА_ВАШ_ТОКЕН на ваш токен"
    echo ""
    exit 1
fi

# Проверяем заполнен ли ID
if grep -q "ВСТАВЬТЕ_ВАШ_ID" .env; then
    echo "❌ ОШИБКА: ID администратора не заполнен!"
    echo ""
    echo "Откройте файл .env и вставьте ваш ID от @userinfobot:"
    echo "  open -e .env"
    echo ""
    echo "Замените ВСТАВЬТЕ_ВАШ_ID на ваш ID"
    echo ""
    exit 1
fi

echo "✅ Файл .env заполнен правильно"
echo ""

# Проверяем Python
if ! command -v python3 &> /dev/null; then
    echo "❌ ОШИБКА: Python3 не установлен!"
    exit 1
fi

echo "✅ Python3 найден"
echo ""

# Создаем виртуальное окружение
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
    echo "✅ Виртуальное окружение создано"
    echo ""
fi

# Активируем
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Устанавливаем зависимости
echo "📥 Установка зависимостей (это займет минуту)..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "✅ Зависимости установлены"
echo ""

# Проверяем есть ли данные в базе
if [ ! -f "lunch_bot.db" ]; then
    echo "🍽️ База данных пуста. Добавляем тестовые данные..."
    echo ""
    python3 add_test_data.py
    echo ""
fi

echo "╔════════════════════════════════════════════════════════╗"
echo "║              🚀 ЗАПУСК БОТА!                           ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "Бот запускается..."
echo "Когда увидите 'Бот запущен и готов к работе!' -"
echo "идите в Telegram и найдите вашего бота!"
echo ""
echo "Для остановки нажмите: Ctrl+C"
echo ""
echo "════════════════════════════════════════════════════════"
echo ""

# Запускаем бота
python3 main.py

