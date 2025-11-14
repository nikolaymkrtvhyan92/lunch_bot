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


# ========== Отправка заказа менеджеру ==========

@admin_only
async def send_order_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /send_order - отправить заказ менеджеру ресторана"""
    poll = db.get_active_poll()
    
    if not poll:
        await update.message.reply_text("❌ Активного голосования нет.")
        return
    
    poll_id = poll['id']
    
    # Получаем победителя голосования
    votes = db.get_poll_votes(poll_id)
    if not votes or all(v[2] == 0 for v in votes):
        await update.message.reply_text("❌ Голосование еще не проведено.")
        return
    
    winner_id = votes[0][0]
    restaurant = db.get_restaurant(winner_id)
    
    if not restaurant:
        await update.message.reply_text("❌ Ресторан-победитель не найден.")
        return
    
    # Получаем все заказы
    all_orders = db.get_all_orders(poll_id)
    
    if not all_orders:
        await update.message.reply_text("❌ Никто еще не сделал заказ.")
        return
    
    # Фильтруем только заказы из ресторана-победителя
    restaurant_orders = [o for o in all_orders if o['restaurant_name'] == restaurant['name']]
    
    if not restaurant_orders:
        await update.message.reply_text(f"❌ Нет заказов для ресторана {restaurant['name']}.")
        return
    
    # Формируем сводку заказов
    order_summary = db.get_order_summary(poll_id)
    
    rest_emoji = restaurant.get('emoji', '🍽️')
    order_text = f"📦 <b>ЗАКАЗ для {rest_emoji} {restaurant['name']}</b>\n\n"
    order_text += f"📅 Дата: {poll['date']}\n"
    order_text += f"👥 Участников: {len(set([o['user_id'] for o in restaurant_orders]))}\n\n"
    
    order_text += "<b>━━━ СВОДКА ЗАКАЗА ━━━</b>\n\n"
    
    total_sum = 0
    for item in order_summary:
        if any(o['menu_item_id'] == item['menu_item_id'] for o in restaurant_orders):
            total = item['price'] * item['total_quantity']
            total_sum += total
            order_text += f"<b>{item['name']}</b> x{item['total_quantity']} = {int(total)}₽\n"
    
    order_text += f"\n💰 <b>ИТОГО: {int(total_sum)}₽</b>\n\n"
    
    order_text += "<b>━━━ ПО УЧАСТНИКАМ ━━━</b>\n\n"
    
    # Группируем по пользователям
    users_orders = {}
    for order in restaurant_orders:
        user_name = order['first_name']
        if user_name not in users_orders:
            users_orders[user_name] = []
        users_orders[user_name].append(order)
    
    for user_name, orders in users_orders.items():
        order_text += f"👤 <b>{user_name}:</b>\n"
        user_total = 0
        for order in orders:
            price = order['price'] * order['quantity']
            user_total += price
            order_text += f"  • {order['dish_name']} x{order['quantity']} — {int(price)}₽\n"
        order_text += f"  💵 Сумма: {int(user_total)}₽\n\n"
    
    # Отправка менеджеру через Telegram (если есть manager_telegram_id)
    manager_id = restaurant.get('manager_telegram_id')
    manager_phone = restaurant.get('manager_phone')
    
    if manager_id:
        try:
            keyboard = [[
                InlineKeyboardButton("✅ Подтвердить заказ", callback_data=f"confirm_order_{poll_id}"),
                InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_order_{poll_id}")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=manager_id,
                text=order_text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            
            await update.message.reply_text(
                f"✅ Заказ отправлен менеджеру {restaurant['name']} в Telegram!\n\n"
                f"📱 Телефон: {manager_phone or 'не указан'}"
            )
        except Exception as e:
            await update.message.reply_text(
                f"❌ Не удалось отправить заказ менеджеру в Telegram.\n"
                f"Ошибка: {str(e)}\n\n"
                f"📱 Свяжитесь с менеджером по телефону: {manager_phone or 'не указан'}"
            )
    elif manager_phone:
        await update.message.reply_text(
            f"📱 Менеджер не добавлен в бота.\n\n"
            f"Позвоните по телефону: <b>{manager_phone}</b>\n\n"
            f"Отправьте ему следующий заказ:\n\n{order_text}",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            f"❌ У ресторана {restaurant['name']} не указаны контакты менеджера.\n\n"
            f"Добавьте контакты через админ-панель и повторите отправку."
        )
    
    # Отправляем админу копию заказа
    await update.message.reply_text(f"📋 Копия заказа:\n\n{order_text}", parse_mode='HTML')


# ========== Подтверждение заказа менеджером ==========

async def confirm_order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Менеджер подтверждает заказ"""
    query = update.callback_query
    await query.answer("✅ Заказ подтверждён!")
    
    poll_id = int(query.data.split('_')[2])
    
    # Уведомляем участников
    participants = db.get_participants(poll_id)
    poll = db.get_poll_by_id(poll_id)
    
    if poll:
        votes = db.get_poll_votes(poll_id)
        if votes:
            winner_id = votes[0][0]
            restaurant = db.get_restaurant(winner_id)
            rest_emoji = restaurant.get('emoji', '🍽️')
            
            notification = (
                f"✅ <b>Заказ подтверждён!</b>\n\n"
                f"Ресторан {rest_emoji} <b>{restaurant['name']}</b> принял ваш заказ.\n"
                f"Ожидайте доставку! 🚚"
            )
            
            for participant in participants:
                try:
                    await context.bot.send_message(
                        chat_id=participant['user_id'],
                        text=notification,
                        parse_mode='HTML'
                    )
                except Exception:
                    pass
    
    await query.edit_message_text(
        f"{query.message.text}\n\n✅ <b>ЗАКАЗ ПОДТВЕРЖДЁН</b>",
        parse_mode='HTML'
    )


async def reject_order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Менеджер отклоняет заказ"""
    query = update.callback_query
    await query.answer("❌ Заказ отклонён")
    
    poll_id = int(query.data.split('_')[2])
    
    # Уведомляем администратора
    try:
        admin_id = int(config.ADMIN_ID)
        await context.bot.send_message(
            chat_id=admin_id,
            text=f"❌ <b>Менеджер отклонил заказ!</b>\n\nСвяжитесь с ним для уточнения деталей.",
            parse_mode='HTML'
        )
    except Exception:
        pass
    
    await query.edit_message_text(
        f"{query.message.text}\n\n❌ <b>ЗАКАЗ ОТКЛОНЁН</b>",
        parse_mode='HTML'
    )

