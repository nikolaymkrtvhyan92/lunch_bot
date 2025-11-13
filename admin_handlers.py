"""
Обработчики команд для администратора
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import Database
import config

db = Database()

# Состояния для ConversationHandler
(RESTAURANT_NAME, RESTAURANT_DESC, RESTAURANT_ADDRESS, RESTAURANT_PHONE, RESTAURANT_EMOJI,
 MENU_RESTAURANT, MENU_ITEM_NAME, MENU_ITEM_PRICE, MENU_ITEM_DESC, MENU_ITEM_CATEGORY) = range(10)


def admin_only(func):
    """Декоратор для проверки прав администратора"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not db.is_admin(user_id):
            await update.message.reply_text("❌ Эта команда доступна только администраторам.")
            return ConversationHandler.END
        return await func(update, context)
    return wrapper


# ========== Панель администратора ==========

@admin_only
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /admin - панель администратора"""
    keyboard = [
        [InlineKeyboardButton("🏪 Рестораны", callback_data="admin_restaurants")],
        [InlineKeyboardButton("📋 Меню", callback_data="admin_menus")],
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("👥 Пользователи", callback_data="admin_users")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    admin_text = """
👑 <b>Панель администратора</b>

Выберите раздел для управления:

🏪 <b>Рестораны</b> - добавление и управление ресторанами
📋 <b>Меню</b> - управление меню ресторанов
📊 <b>Статистика</b> - статистика голосований
👥 <b>Пользователи</b> - список пользователей

<b>Быстрые команды:</b>
/add_restaurant - Добавить ресторан
/list_restaurants - Список всех ресторанов
/add_menu - Добавить блюдо в меню
"""
    
    await update.message.reply_text(admin_text, reply_markup=reply_markup, parse_mode='HTML')


# ========== Управление ресторанами ==========

@admin_only
async def add_restaurant_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /add_restaurant - начать добавление ресторана"""
    await update.message.reply_text(
        "🏪 <b>Добавление нового ресторана</b>\n\n"
        "Введите название ресторана:\n"
        "(Отправьте /cancel для отмены)",
        parse_mode='HTML'
    )
    return RESTAURANT_NAME


async def restaurant_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить название ресторана"""
    context.user_data['restaurant_name'] = update.message.text
    
    await update.message.reply_text(
        "📝 Введите описание ресторана:\n"
        "(Или отправьте /skip чтобы пропустить)"
    )
    return RESTAURANT_DESC


async def restaurant_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить описание ресторана"""
    if update.message.text != '/skip':
        context.user_data['restaurant_desc'] = update.message.text
    else:
        context.user_data['restaurant_desc'] = None
    
    await update.message.reply_text(
        "📍 Введите адрес ресторана:\n"
        "(Или отправьте /skip чтобы пропустить)"
    )
    return RESTAURANT_ADDRESS


async def restaurant_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить адрес ресторана"""
    if update.message.text != '/skip':
        context.user_data['restaurant_address'] = update.message.text
    else:
        context.user_data['restaurant_address'] = None
    
    await update.message.reply_text(
        "📞 Введите телефон ресторана:\n"
        "(Или отправьте /skip чтобы пропустить)"
    )
    return RESTAURANT_PHONE


async def restaurant_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить телефон ресторана"""
    if update.message.text != '/skip':
        context.user_data['restaurant_phone'] = update.message.text
    else:
        context.user_data['restaurant_phone'] = None
    
    await update.message.reply_text(
        "😊 Введите emoji для ресторана (например: 🍕 🍔 🍝 🍣)\n\n"
        "Популярные emoji:\n"
        "🥘 - Армянская/восточная кухня\n"
        "🍔 - Бургерная\n"
        "🍝 - Итальянская кухня\n"
        "🍣 - Суши/японская кухня\n"
        "🍕 - Пиццерия\n"
        "🌮 - Мексиканская кухня\n"
        "🥡 - Китайская кухня\n"
        "🫓 - Грузинская кухня\n"
        "🍰 - Десерты/кафе\n\n"
        "(Или отправьте /skip для 🍽️ по умолчанию)"
    )
    return RESTAURANT_EMOJI


async def restaurant_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить emoji и сохранить ресторан"""
    if update.message.text != '/skip':
        context.user_data['restaurant_emoji'] = update.message.text
    else:
        context.user_data['restaurant_emoji'] = '🍽️'
    
    # Сохраняем ресторан
    restaurant_id = db.add_restaurant(
        name=context.user_data['restaurant_name'],
        description=context.user_data.get('restaurant_desc'),
        address=context.user_data.get('restaurant_address'),
        phone=context.user_data.get('restaurant_phone'),
        emoji=context.user_data.get('restaurant_emoji', '🍽️')
    )
    
    restaurant_name = context.user_data['restaurant_name']
    restaurant_emoji = context.user_data.get('restaurant_emoji', '🍽️')
    
    # Очищаем данные
    context.user_data.clear()
    
    await update.message.reply_text(
        f"✅ Ресторан {restaurant_emoji} <b>{restaurant_name}</b> успешно добавлен!\n\n"
        f"Теперь вы можете добавить меню командой:\n"
        f"/add_menu",
        parse_mode='HTML'
    )
    
    return ConversationHandler.END


@admin_only
async def list_restaurants_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /list_restaurants - список всех ресторанов"""
    restaurants = db.get_all_restaurants(active_only=False)
    
    if not restaurants:
        await update.message.reply_text("❌ Рестораны не найдены.")
        return
    
    text = "🏪 <b>Список ресторанов:</b>\n\n"
    
    for restaurant in restaurants:
        status = "✅" if restaurant['is_active'] else "❌"
        text += f"{status} <b>{restaurant['name']}</b> (ID: {restaurant['id']})\n"
        if restaurant['description']:
            text += f"   📝 {restaurant['description']}\n"
        if restaurant['address']:
            text += f"   📍 {restaurant['address']}\n"
        if restaurant['phone']:
            text += f"   📞 {restaurant['phone']}\n"
        text += "\n"
    
    await update.message.reply_text(text, parse_mode='HTML')


# ========== Управление меню ==========

@admin_only
async def add_menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /add_menu - начать добавление блюда в меню"""
    restaurants = db.get_all_restaurants()
    
    if not restaurants:
        await update.message.reply_text(
            "❌ Сначала добавьте хотя бы один ресторан: /add_restaurant"
        )
        return ConversationHandler.END
    
    keyboard = []
    for restaurant in restaurants:
        keyboard.append([
            InlineKeyboardButton(
                f"{restaurant['name']}", 
                callback_data=f"addmenu_{restaurant['id']}"
            )
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📋 <b>Добавление блюда в меню</b>\n\n"
        "Выберите ресторан:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    
    return MENU_RESTAURANT


async def menu_restaurant_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ресторан выбран"""
    query = update.callback_query
    await query.answer()
    
    restaurant_id = int(query.data.split('_')[1])
    context.user_data['menu_restaurant_id'] = restaurant_id
    
    restaurant = db.get_restaurant(restaurant_id)
    
    await query.edit_message_text(
        f"✅ Выбран ресторан: <b>{restaurant['name']}</b>\n\n"
        f"Введите название блюда:",
        parse_mode='HTML'
    )
    
    return MENU_ITEM_NAME


async def menu_item_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить название блюда"""
    context.user_data['menu_item_name'] = update.message.text
    
    await update.message.reply_text(
        "💰 Введите цену блюда (в рублях):\n"
        "Например: 350 или 450.50"
    )
    return MENU_ITEM_PRICE


async def menu_item_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить цену блюда"""
    try:
        price = float(update.message.text.replace(',', '.'))
        context.user_data['menu_item_price'] = price
        
        await update.message.reply_text(
            "📝 Введите описание блюда:\n"
            "(Или отправьте /skip чтобы пропустить)"
        )
        return MENU_ITEM_DESC
    except ValueError:
        await update.message.reply_text(
            "❌ Неверный формат цены. Введите число (например: 350 или 450.50)"
        )
        return MENU_ITEM_PRICE


async def menu_item_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить описание блюда"""
    if update.message.text != '/skip':
        context.user_data['menu_item_desc'] = update.message.text
    else:
        context.user_data['menu_item_desc'] = None
    
    await update.message.reply_text(
        "📂 Введите категорию блюда:\n"
        "Например: Салаты, Основные блюда, Десерты, Напитки\n"
        "(Или отправьте /skip чтобы пропустить)"
    )
    return MENU_ITEM_CATEGORY


async def menu_item_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить категорию и сохранить блюдо"""
    if update.message.text != '/skip':
        context.user_data['menu_item_category'] = update.message.text
    else:
        context.user_data['menu_item_category'] = None
    
    # Сохраняем блюдо
    item_id = db.add_menu_item(
        restaurant_id=context.user_data['menu_restaurant_id'],
        name=context.user_data['menu_item_name'],
        price=context.user_data['menu_item_price'],
        description=context.user_data.get('menu_item_desc'),
        category=context.user_data.get('menu_item_category')
    )
    
    item_name = context.user_data['menu_item_name']
    item_price = context.user_data['menu_item_price']
    
    # Очищаем данные
    restaurant_id = context.user_data['menu_restaurant_id']
    context.user_data.clear()
    
    keyboard = [[
        InlineKeyboardButton("➕ Добавить еще блюдо", callback_data=f"addmenu_{restaurant_id}")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✅ Блюдо <b>{item_name}</b> ({item_price} ₽) успешно добавлено!\n\n"
        f"Хотите добавить еще блюдо?",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    
    return ConversationHandler.END


# ========== Статистика ==========

async def admin_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать статистику"""
    query = update.callback_query
    await query.answer()
    
    # Получаем статистику
    restaurants = db.get_all_restaurants()
    users = db.get_all_users()
    
    stats_text = "📊 <b>Статистика</b>\n\n"
    stats_text += f"🏪 Всего ресторанов: {len(restaurants)}\n"
    stats_text += f"👥 Всего пользователей: {len(users)}\n"
    
    # Добавить больше статистики по необходимости
    
    await query.edit_message_text(stats_text, parse_mode='HTML')


async def admin_users_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать пользователей"""
    query = update.callback_query
    await query.answer()
    
    users = db.get_all_users()
    
    if not users:
        await query.edit_message_text("❌ Пользователи не найдены.")
        return
    
    users_text = "👥 <b>Пользователи бота:</b>\n\n"
    
    for user in users[:20]:  # Показываем первых 20
        name = user['first_name']
        if user['last_name']:
            name += f" {user['last_name']}"
        username = f" (@{user['username']})" if user['username'] else ""
        admin_mark = " 👑" if user['is_admin'] else ""
        users_text += f"• {name}{username}{admin_mark}\n"
    
    if len(users) > 20:
        users_text += f"\n... и еще {len(users) - 20} пользователей"
    
    users_text += f"\n\n<b>Всего: {len(users)}</b>"
    
    await query.edit_message_text(users_text, parse_mode='HTML')


# ========== Отмена ==========

async def cancel_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена операции"""
    context.user_data.clear()
    await update.message.reply_text("❌ Операция отменена.")
    return ConversationHandler.END

