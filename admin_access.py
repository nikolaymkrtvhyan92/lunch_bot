"""
Админ команды для управления доступом пользователей
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from admin_handlers import admin_only
import config

db = Database()


@admin_only
async def add_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /add_user - добавить пользователя в whitelist"""
    
    if not context.args:
        text = """
👥 <b>Добавить пользователя</b>

<b>Использование:</b>
/add_user @username
/add_user 123456789 (Telegram ID)

<b>Примеры:</b>
/add_user @john_doe
/add_user 987654321
"""
        await update.message.reply_text(text, parse_mode='HTML')
        return
    
    identifier = context.args[0]
    
    # Если это ID
    if identifier.isdigit():
        user_id = int(identifier)
        db.approve_user(user_id)
        
        text = f"""
✅ <b>Пользователь одобрен!</b>

ID: <code>{user_id}</code>

Пользователь получит доступ к боту.
"""
        await update.message.reply_text(text, parse_mode='HTML')
        
        # Отправляем уведомление пользователю
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="""
🎉 <b>Доступ предоставлен!</b>

Ваш запрос на доступ к боту Инкубатор одобрен!

Теперь вы можете пользоваться ботом.

Отправьте /start чтобы начать.
""",
                parse_mode='HTML'
            )
        except:
            pass
    
    else:
        text = """
❌ <b>Ошибка</b>

Укажите Telegram ID пользователя (число).

Чтобы узнать ID, попросите пользователя отправить /start боту, после чего вы получите уведомление с его ID.
"""
        await update.message.reply_text(text, parse_mode='HTML')


@admin_only
async def remove_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /remove_user - удалить пользователя из whitelist"""
    
    if not context.args:
        text = """
🚫 <b>Удалить пользователя</b>

<b>Использование:</b>
/remove_user 123456789 (Telegram ID)

<b>Пример:</b>
/remove_user 987654321
"""
        await update.message.reply_text(text, parse_mode='HTML')
        return
    
    identifier = context.args[0]
    
    if identifier.isdigit():
        user_id = int(identifier)
        db.reject_user(user_id)
        
        text = f"""
✅ <b>Доступ отозван!</b>

ID: <code>{user_id}</code>

Пользователь больше не сможет использовать бота.
"""
        await update.message.reply_text(text, parse_mode='HTML')
    else:
        text = "❌ Укажите Telegram ID пользователя (число)."
        await update.message.reply_text(text)


@admin_only
async def list_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /list_users - список всех пользователей"""
    
    users = db.get_all_users_list()
    pending = db.get_pending_users()
    
    text = "👥 <b>ПОЛЬЗОВАТЕЛИ БОТА</b>\n\n"
    
    # Статистика
    approved_count = sum(1 for u in users if u['access_status'] == 'approved')
    pending_count = len(pending)
    rejected_count = sum(1 for u in users if u['access_status'] == 'rejected')
    
    text += f"📊 <b>Статистика:</b>\n"
    text += f"✅ Одобрено: {approved_count}\n"
    text += f"⏳ На рассмотрении: {pending_count}\n"
    text += f"❌ Отклонено: {rejected_count}\n"
    text += f"👤 Всего: {len(users)}\n\n"
    
    # Ожидают одобрения
    if pending:
        text += "⏳ <b>Ожидают одобрения:</b>\n"
        for user in pending[:5]:  # Первые 5
            name = user['first_name'] or "Без имени"
            username = f"@{user['username']}" if user['username'] else "без username"
            dept = f" ({user['department']})" if user['department'] else ""
            text += f"• {name} {username}{dept}\n"
            text += f"  ID: <code>{user['user_id']}</code>\n"
        if len(pending) > 5:
            text += f"... и ещё {len(pending) - 5}\n"
        text += "\n"
    
    # Одобренные
    approved_users = [u for u in users if u['access_status'] == 'approved']
    if approved_users:
        text += f"✅ <b>Одобренные ({len(approved_users)}):</b>\n"
        for user in approved_users[:10]:  # Первые 10
            name = user['first_name'] or "Без имени"
            username = f"@{user['username']}" if user['username'] else ""
            dept = f" - {user['department']}" if user['department'] else ""
            text += f"• {name} {username}{dept}\n"
        if len(approved_users) > 10:
            text += f"... и ещё {len(approved_users) - 10}\n"
    
    keyboard = [
        [InlineKeyboardButton("⏳ Запросы на одобрение", callback_data="pending_users")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)


async def pending_users_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать пользователей ожидающих одобрения"""
    query = update.callback_query
    await query.answer()
    
    pending = db.get_pending_users()
    
    if not pending:
        text = "✅ <b>Нет запросов на одобрение</b>\n\nВсе запросы обработаны!"
        await query.edit_message_text(text, parse_mode='HTML')
        return
    
    text = f"⏳ <b>ЗАПРОСЫ НА ОДОБРЕНИЕ ({len(pending)})</b>\n\n"
    
    for user in pending:
        name = f"{user['first_name']} {user['last_name'] or ''}".strip()
        username = f"@{user['username']}" if user['username'] else "без username"
        dept = f"\n🏢 Отдел: {user['department']}" if user['department'] else ""
        
        text += f"━━━━━━━━━━━━━━━━\n"
        text += f"👤 <b>{name}</b>\n"
        text += f"Username: {username}\n"
        text += f"ID: <code>{user['user_id']}</code>{dept}\n\n"
    
    text += "━━━━━━━━━━━━━━━━\n\n"
    text += "Используйте:\n"
    text += "• /add_user ID - одобрить\n"
    text += "• /remove_user ID - отклонить"
    
    keyboard = [
        [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)


async def approve_user_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Одобрить пользователя через кнопку"""
    query = update.callback_query
    
    # Извлекаем user_id из callback_data: approve_user_123456
    user_id = int(query.data.split('_')[2])
    
    # Одобряем
    db.approve_user(user_id)
    
    await query.answer("✅ Пользователь одобрен!")
    
    # Обновляем сообщение
    text = query.message.text + "\n\n✅ <b>ОДОБРЕНО</b>"
    await query.edit_message_text(text, parse_mode='HTML')
    
    # Отправляем уведомление пользователю
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text="""
🎉 <b>Доступ предоставлен!</b>

Ваш запрос на доступ к боту Инкубатор одобрен!

Теперь вы можете пользоваться ботом.

Отправьте /start чтобы начать.
""",
            parse_mode='HTML'
        )
    except Exception as e:
        print(f"Error notifying user {user_id}: {e}")


async def reject_user_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отклонить пользователя через кнопку"""
    query = update.callback_query
    
    # Извлекаем user_id
    user_id = int(query.data.split('_')[2])
    
    # Отклоняем
    db.reject_user(user_id)
    
    await query.answer("❌ Пользователь отклонён")
    
    # Обновляем сообщение
    text = query.message.text + "\n\n❌ <b>ОТКЛОНЕНО</b>"
    await query.edit_message_text(text, parse_mode='HTML')

