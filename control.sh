#!/bin/bash

BOT_DIR="/Users/sevak.martirosyan/lunch_bot"

case "$1" in
    start)
        echo "🚀 Запуск бота..."
        cd "$BOT_DIR"
        if ps aux | grep "python.*main.py" | grep -v grep > /dev/null; then
            echo "⚠️  Бот уже запущен!"
            exit 1
        fi
        ./START_HERE.sh
        ;;
    
    stop)
        echo "🛑 Остановка бота..."
        if pkill -f "python.*main.py"; then
            echo "✅ Бот остановлен"
        else
            echo "❌ Бот не был запущен"
        fi
        ;;
    
    restart)
        echo "🔄 Перезапуск бота..."
        pkill -f "python.*main.py" 2>/dev/null
        sleep 2
        cd "$BOT_DIR"
        ./START_HERE.sh
        ;;
    
    status)
        if ps aux | grep "python.*main.py" | grep -v grep > /dev/null; then
            echo "✅ Бот работает"
            ps aux | grep "python.*main.py" | grep -v grep
        else
            echo "❌ Бот не запущен"
        fi
        ;;
    
    logs)
        echo "📋 Логи бота:"
        if [ -f "$BOT_DIR/bot.log" ]; then
            tail -50 "$BOT_DIR/bot.log"
        else
            echo "❌ Файл логов не найден"
        fi
        ;;
    
    *)
        echo "╔════════════════════════════════════════════════════════╗"
        echo "║         🍽️  УПРАВЛЕНИЕ БОТОМ  🍽️                     ║"
        echo "╚════════════════════════════════════════════════════════╝"
        echo ""
        echo "Использование: ./control.sh [команда]"
        echo ""
        echo "Доступные команды:"
        echo "  start    - Запустить бота"
        echo "  stop     - Остановить бота"
        echo "  restart  - Перезапустить бота"
        echo "  status   - Проверить статус бота"
        echo "  logs     - Показать последние 50 строк логов"
        echo ""
        echo "Примеры:"
        echo "  ./control.sh start"
        echo "  ./control.sh stop"
        echo "  ./control.sh status"
        exit 1
        ;;
esac

