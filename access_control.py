"""
Система контроля доступа к боту (Whitelist)
"""
from functools import wraps
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import Database
import config

db = Database()

# Состояния для ConversationHandler
REQUEST_DEPARTMENT = 1


def require_access(func):
    """
    Декоратор для проверки доступа к боту
    Разрешает доступ только одобренным пользователям
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        
        # Админ всегда имеет доступ
        if user.id == int(config.ADMIN_ID):
            return await func(update, context, *args, **kwargs)
        
        # Проверяем статус доступа
        status = db.get_user_access_status(user.id)
        
        if status == 'approved':
            # Доступ разрешен
            return await func(update, context, *args, **kwargs)
        
        elif status == 'pending':
            # Запрос на рассмотрении
            text = """
🔒 <b>Запрос на рассмотрении</b>

Ваш запрос на доступ к боту отправлен администратору.

⏳ Ожидайте одобрения.

Вы получите уведомление когда доступ будет предоставлен.
"""
            if update.callback_query:
                await update.callback_query.answer(text[:200], show_alert=True)
            else:
                await update.message.reply_text(text, parse_mode='HTML')
            return
        
        elif status == 'rejected':
            # Доступ отклонен
            text = """
❌ <b>Доступ отклонён</b>

К сожалению, ваш запрос на доступ к боту был отклонён администратором.

Если вы считаете это ошибкой, свяжитесь с администратором компании.
"""
            if update.callback_query:
                await update.callback_query.answer(text[:200], show_alert=True)
            else:
                await update.message.reply_text(text, parse_mode='HTML')
            return
        
        else:
            # Нет запроса - показываем форму
            return await show_access_request_form(update, context)
    
    return wrapper


async def show_access_request_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать форму запроса доступа"""
    user = update.effective_user
    
    text = f"""
🔒 <b>Приватный бот компании Инкубатор</b>

Этот бот доступен только для сотрудников компании.

Хотите запросить доступ?

👤 <b>Ваши данные:</b>
Имя: {user.first_name} {user.last_name or ''}
Username: @{user.username or 'не указан'}
"""
    
    keyboard = [
        [InlineKeyboardButton("📝 Запросить доступ", callback_data="request_access")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel_access")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Проверяем тип update - message или callback query
    if update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)


async def request_access_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка запроса доступа"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    
    # Добавляем пользователя в БД если его нет
    db.add_user(
        user_id=user.id,
        username=user.username or "",
        first_name=user.first_name or "",
        last_name=user.last_name or ""
    )
    
    text = """
📝 <b>Запрос доступа</b>

Укажите ваш отдел (например: IT, HR, Маркетинг, или напишите "-" чтобы пропустить):
"""
    
    await query.edit_message_text(text, parse_mode='HTML')
    return REQUEST_DEPARTMENT


async def receive_department(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить отдел от пользователя"""
    user = update.effective_user
    department = update.message.text
    
    if department == "-":
        department = None
    
    # Отправляем запрос
    db.request_access(user.id, department)
    
    # Отправляем уведомление админу
    await notify_admin_about_request(context, user, department)
    
    text = """
✅ <b>Запрос отправлен!</b>

Ваш запрос на доступ к боту отправлен администратору.

⏳ Ожидайте одобрения. Вы получите уведомление.

Обычно это занимает несколько минут.
"""
    
    await update.message.reply_text(text, parse_mode='HTML')
    return ConversationHandler.END


async def notify_admin_about_request(context: ContextTypes.DEFAULT_TYPE, user, department: str = None):
    """Отправить уведомление админу о новом запросе"""
    text = f"""
🔔 <b>Новый запрос доступа!</b>

👤 <b>Пользователь:</b>
Имя: {user.first_name} {user.last_name or ''}
Username: @{user.username or 'не указан'}
ID: <code>{user.id}</code>
"""
    
    if department:
        text += f"🏢 Отдел: {department}\n"
    
    text += "\n<b>Действия:</b>"
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_user_{user.id}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_user_{user.id}")
        ],
        [InlineKeyboardButton("👥 Все запросы", callback_data="pending_users")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await context.bot.send_message(
            chat_id=config.ADMIN_ID,
            text=text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    except Exception as e:
        print(f"Error sending notification to admin: {e}")


async def cancel_access_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена запроса доступа"""
    query = update.callback_query
    await query.answer()
    
    text = """
❌ <b>Отменено</b>

Запрос доступа отменён.

Если передумаете - отправьте /start снова.
"""
    
    await query.edit_message_text(text, parse_mode='HTML')
    return ConversationHandler.END

