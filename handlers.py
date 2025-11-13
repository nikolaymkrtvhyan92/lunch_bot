"""
Обработчики команд бота
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from datetime import datetime

db = Database()


# ========== Общие команды ==========

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - регистрация пользователя"""
    user = update.effective_user
    
    # Добавляем пользователя в БД
    db.add_user(
        user_id=user.id,
        username=user.username or "",
        first_name=user.first_name or "",
        last_name=user.last_name or ""
    )
    
    welcome_text = f"""
Привет, {user.first_name}! 👋

Я помогу организовать совместный обед для вашей команды! 🍽️✨

<b>🎯 Что я умею:</b>
• Голосование за рестораны
• Показываю меню с ценами  
• Веду список участников
• Отправляю напоминания

<b>🚀 Начнём?</b>
Используй /lunch чтобы выбрать ресторан!

<b>📋 Все команды:</b>
/lunch - Голосование за ресторан
/menu - Меню ресторанов
/participants - Кто идёт на обед
/results - Результаты голосования
/help - Подробная справка

Приятного аппетита! 😋
"""
    
    await update.message.reply_text(welcome_text, parse_mode='HTML')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    help_text = """
📖 <b>Помощь по использованию бота</b>

<b>Как организовать обед:</b>
1. Запустите голосование командой /lunch
2. Выберите ресторан (inline кнопки)
3. Запишитесь на обед командой /join
4. Посмотрите результаты /results

<b>Полезные команды:</b>
/menu - Посмотреть меню ресторана
/participants - Кто идет на обед
/cancel - Отменить участие в обеде

<b>Для администраторов:</b>
/admin - Управление ресторанами и меню
"""
    
    await update.message.reply_text(help_text, parse_mode='HTML')


# ========== Голосование ==========

async def lunch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /lunch - начать голосование"""
    user_id = update.effective_user.id
    
    # Проверяем, есть ли уже активное голосование
    active_poll = db.get_active_poll()
    
    if not active_poll:
        # Создаем новое голосование
        poll_id = db.create_poll(user_id)
        context.user_data['current_poll_id'] = poll_id
    else:
        poll_id = active_poll['id']
        context.user_data['current_poll_id'] = poll_id
    
    # Получаем список ресторанов
    restaurants = db.get_all_restaurants()
    
    if not restaurants:
        await update.message.reply_text(
            "❌ К сожалению, пока нет доступных ресторанов.\n"
            "Попросите администратора добавить рестораны."
        )
        return
    
    # Создаем клавиатуру с ресторанами
    keyboard = []
    for restaurant in restaurants:
        # Используем emoji из базы данных (или дефолтный если нет)
        emoji = restaurant.get('emoji', '🍽️')
        keyboard.append([
            InlineKeyboardButton(
                f"{emoji} {restaurant['name']}", 
                callback_data=f"vote_{restaurant['id']}"
            )
        ])
    
    # Добавляем кнопки управления (улучшенный порядок)
    keyboard.append([
        InlineKeyboardButton("👥 Участники", callback_data="show_participants"),
        InlineKeyboardButton("📊 Результаты", callback_data="show_results")
    ])
    keyboard.append([
        InlineKeyboardButton("📋 Меню ресторанов", callback_data="show_menu_list")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Получаем текущие голоса
    user_vote = db.get_user_vote(poll_id, user_id)
    vote_text = ""
    if user_vote:
        restaurant = db.get_restaurant(user_vote)
        if restaurant:
            rest_emoji = restaurant.get('emoji', '🍽️')
            vote_text = f"\n\n✅ Ваш выбор: {rest_emoji} <b>{restaurant['name']}</b>"
    
    await update.message.reply_text(
        f"🍽️ <b>Время выбирать обед!</b>\n\n"
        f"Куда пойдём сегодня? Голосуйте! 🎯{vote_text}",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def vote_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка голосования"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    restaurant_id = int(query.data.split('_')[1])
    
    # Получаем активное голосование
    poll = db.get_active_poll()
    if not poll:
        keyboard = [[
            InlineKeyboardButton("🏠 К голосованию", callback_data="back_to_voting")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("❌ Голосование не найдено. Начните новое: /lunch", reply_markup=reply_markup)
        return
    
    poll_id = poll['id']
    
    # Добавляем голос
    db.add_vote(poll_id, user_id, restaurant_id)
    
    # Автоматически записываем на обед
    db.add_participant(poll_id, user_id)
    
    # Получаем информацию о ресторане
    restaurant = db.get_restaurant(restaurant_id)
    rest_emoji = restaurant.get('emoji', '🍽️')
    
    # Добавляем кнопки для перехода к результатам или возврата к голосованию
    keyboard = [
        [
            InlineKeyboardButton("📊 Результаты", callback_data="show_results"),
            InlineKeyboardButton("👥 Участники", callback_data="show_participants")
        ],
        [InlineKeyboardButton("🏠 К голосованию", callback_data="back_to_voting")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"✅ Отлично! Вы выбрали {rest_emoji} <b>{restaurant['name']}</b>\n\n"
        f"Вы автоматически записаны на обед! 🎉",
        parse_mode='HTML',
        reply_markup=reply_markup
    )


async def results_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /results - показать результаты голосования"""
    poll = db.get_active_poll()
    
    if not poll:
        await update.message.reply_text("❌ Сегодня голосование еще не начато. Используйте /lunch")
        return
    
    poll_id = poll['id']
    votes = db.get_poll_votes(poll_id)
    participants = db.get_participants(poll_id)
    
    if not votes or all(v[2] == 0 for v in votes):
        await update.message.reply_text("📊 Пока никто не проголосовал.")
        return
    
    result_text = "📊 <b>Результаты голосования:</b>\n\n"
    
    for idx, (rest_id, rest_name, vote_count) in enumerate(votes, 1):
        if vote_count > 0:
            bar = "🟩" * vote_count + "⬜" * (len(participants) - vote_count) if participants else "🟩" * vote_count
            result_text += f"{idx}. <b>{rest_name}</b>\n   {bar} {vote_count} голос(ов)\n\n"
    
    result_text += f"\n👥 Участников обеда: {len(participants)}\n"
    
    # Добавляем кнопку для просмотра меню победителя
    if votes and votes[0][2] > 0:
        winner_id = votes[0][0]
        winner_name = votes[0][1]
        result_text += f"\n🏆 Лидирует: <b>{winner_name}</b>"
        
        keyboard = [[
            InlineKeyboardButton("📋 Меню победителя", callback_data=f"menu_{winner_id}")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(result_text, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text(result_text, parse_mode='HTML')


async def show_results_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать результаты через callback"""
    query = update.callback_query
    await query.answer()
    
    poll = db.get_active_poll()
    
    if not poll:
        keyboard = [[
            InlineKeyboardButton("🏠 На главную", callback_data="back_to_voting")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("❌ Голосование не найдено.", reply_markup=reply_markup)
        return
    
    poll_id = poll['id']
    votes = db.get_poll_votes(poll_id)
    participants = db.get_participants(poll_id)
    
    if not votes or all(v[2] == 0 for v in votes):
        keyboard = [[
            InlineKeyboardButton("🏠 К голосованию", callback_data="back_to_voting")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("📊 Пока никто не проголосовал.", reply_markup=reply_markup)
        return
    
    result_text = "📊 <b>Результаты голосования:</b>\n\n"
    
    for idx, (rest_id, rest_name, vote_count) in enumerate(votes, 1):
        if vote_count > 0:
            # Получаем emoji для ресторана
            restaurant = db.get_restaurant(rest_id)
            rest_emoji = restaurant.get('emoji', '🍽️') if restaurant else '🍽️'
            bar = "🟩" * vote_count
            result_text += f"{idx}. {rest_emoji} <b>{rest_name}</b>: {bar} {vote_count}\n"
    
    result_text += f"\n👥 Участников: {len(participants)}"
    
    # Добавляем кнопку возврата к голосованию
    keyboard = [[
        InlineKeyboardButton("👥 Участники", callback_data="show_participants"),
        InlineKeyboardButton("🏠 К голосованию", callback_data="back_to_voting")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(result_text, parse_mode='HTML', reply_markup=reply_markup)


# ========== Участники ==========

async def join_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /join - записаться на обед"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    poll = db.get_active_poll()
    
    if not poll:
        await update.message.reply_text("❌ Сегодня голосование еще не начато. Используйте /lunch")
        return
    
    poll_id = poll['id']
    
    # Проверяем, уже записан ли пользователь
    if db.is_participant(poll_id, user_id):
        keyboard = [[
            InlineKeyboardButton("❌ Отменить участие", callback_data="leave_lunch")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"✅ {user_name}, вы уже записаны на обед!",
            reply_markup=reply_markup
        )
        return
    
    # Записываем на обед
    db.add_participant(poll_id, user_id)
    
    participants = db.get_participants(poll_id)
    
    await update.message.reply_text(
        f"✅ {user_name}, вы записаны на обед!\n"
        f"👥 Всего участников: {len(participants)}\n\n"
        f"Не забудьте проголосовать: /lunch"
    )


async def participants_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /participants - список участников"""
    poll = db.get_active_poll()
    
    if not poll:
        await update.message.reply_text("❌ Сегодня голосование еще не начато.")
        return
    
    poll_id = poll['id']
    participants = db.get_participants(poll_id)
    
    if not participants:
        await update.message.reply_text("👥 Пока никто не записался на обед.")
        return
    
    participants_text = "👥 <b>Участники обеда:</b>\n\n"
    
    for idx, participant in enumerate(participants, 1):
        name = participant['first_name']
        if participant['last_name']:
            name += f" {participant['last_name']}"
        username = f" (@{participant['username']})" if participant['username'] else ""
        participants_text += f"{idx}. {name}{username}\n"
    
    participants_text += f"\n<b>Всего: {len(participants)} человек</b>"
    
    await update.message.reply_text(participants_text, parse_mode='HTML')


async def show_participants_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать участников через callback"""
    query = update.callback_query
    await query.answer()
    
    poll = db.get_active_poll()
    
    if not poll:
        keyboard = [[
            InlineKeyboardButton("🏠 К голосованию", callback_data="back_to_voting")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("❌ Голосование не найдено.", reply_markup=reply_markup)
        return
    
    poll_id = poll['id']
    participants = db.get_participants(poll_id)
    
    if not participants:
        keyboard = [[
            InlineKeyboardButton("🏠 К голосованию", callback_data="back_to_voting")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("👥 Пока никто не записался.", reply_markup=reply_markup)
        return
    
    participants_text = "👥 <b>Участники:</b>\n\n"
    
    for idx, participant in enumerate(participants, 1):
        name = participant['first_name']
        participants_text += f"{idx}. {name}\n"
    
    participants_text += f"\n<b>Всего: {len(participants)}</b>"
    
    # Добавляем кнопку возврата к голосованию
    keyboard = [[
        InlineKeyboardButton("🏠 К голосованию", callback_data="back_to_voting")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(participants_text, parse_mode='HTML', reply_markup=reply_markup)


async def leave_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменить участие в обеде"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    poll = db.get_active_poll()
    
    if not poll:
        keyboard = [[
            InlineKeyboardButton("🏠 К голосованию", callback_data="back_to_voting")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("❌ Голосование не найдено.", reply_markup=reply_markup)
        return
    
    poll_id = poll['id']
    db.remove_participant(poll_id, user_id)
    
    keyboard = [[
        InlineKeyboardButton("🏠 К голосованию", callback_data="back_to_voting")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("✅ Вы отменили участие в обеде.", reply_markup=reply_markup)


# ========== Меню ==========

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /menu - показать меню ресторана"""
    restaurants = db.get_all_restaurants()
    
    if not restaurants:
        await update.message.reply_text("❌ Нет доступных ресторанов.")
        return
    
    keyboard = []
    for restaurant in restaurants:
        keyboard.append([
            InlineKeyboardButton(
                f"📋 {restaurant['name']}", 
                callback_data=f"menu_{restaurant['id']}"
            )
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📋 <b>Выберите ресторан для просмотра меню:</b>",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def show_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать меню ресторана"""
    query = update.callback_query
    await query.answer()
    
    restaurant_id = int(query.data.split('_')[1])
    restaurant = db.get_restaurant(restaurant_id)
    
    if not restaurant:
        await query.edit_message_text("❌ Ресторан не найден.")
        return
    
    menu_items = db.get_restaurant_menu(restaurant_id)
    
    if not menu_items:
        keyboard = [[
            InlineKeyboardButton("🏠 На главную", callback_data="back_to_main")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"📋 <b>{restaurant['name']}</b>\n\n"
            f"❌ Меню пока не добавлено.",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        return
    
    # Группируем по категориям
    categories = {}
    for item in menu_items:
        category = item['category'] or 'Основное меню'
        if category not in categories:
            categories[category] = []
        categories[category].append(item)
    
    # Создаем кнопки для выбора категории
    keyboard = []
    for category in categories.keys():
        keyboard.append([
            InlineKeyboardButton(f"📂 {category}", callback_data=f"category_{restaurant_id}_{category}")
        ])
    
    keyboard.append([
        InlineKeyboardButton("🏠 К голосованию", callback_data="back_to_voting")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    menu_header = f"📋 <b>Меню: {restaurant['name']}</b>\n\n"
    if restaurant['address']:
        menu_header += f"📍 {restaurant['address']}\n"
    if restaurant['phone']:
        menu_header += f"📞 {restaurant['phone']}\n"
    menu_header += f"\n<i>Выберите категорию:</i>"
    
    await query.edit_message_text(menu_header, parse_mode='HTML', reply_markup=reply_markup)


async def show_category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать блюда из выбранной категории"""
    query = update.callback_query
    await query.answer()
    
    # Разбираем callback_data: category_restaurant_id_category_name
    parts = query.data.split('_', 2)
    restaurant_id = int(parts[1])
    category = parts[2]
    
    restaurant = db.get_restaurant(restaurant_id)
    if not restaurant:
        await query.edit_message_text("❌ Ресторан не найден.")
        return
    
    menu_items = db.get_restaurant_menu(restaurant_id)
    
    # Фильтруем по категории
    category_items = [item for item in menu_items if (item['category'] or 'Основное меню') == category]
    
    if not category_items:
        keyboard = [[
            InlineKeyboardButton("◀️ Назад к меню", callback_data=f"menu_{restaurant_id}")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("❌ В этой категории пока нет блюд.", reply_markup=reply_markup)
        return
    
    menu_text = f"📋 <b>{restaurant['name']}</b>\n"
    menu_text += f"📂 <b>{category}</b>\n\n"
    menu_text += "<i>Нажмите на блюдо, чтобы добавить в заказ:</i>\n\n"
    
    # Создаем кнопки для каждого блюда
    keyboard = []
    for item in category_items:
        price = f"{item['price']:.0f} ₽" if item['price'] else ""
        button_text = f"{item['name']} - {price}"
        # Ограничиваем длину текста кнопки
        if len(button_text) > 60:
            button_text = button_text[:57] + "..."
        keyboard.append([
            InlineKeyboardButton(button_text, callback_data=f"order_{item['id']}")
        ])
    
    # Добавляем кнопки навигации
    keyboard.append([
        InlineKeyboardButton("🛒 Мой заказ", callback_data="my_orders"),
        InlineKeyboardButton("◀️ Назад", callback_data=f"menu_{restaurant_id}")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(menu_text, parse_mode='HTML', reply_markup=reply_markup)


async def add_order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавить блюдо в заказ"""
    query = update.callback_query
    await query.answer()
    
    menu_item_id = int(query.data.split('_')[1])
    user_id = update.effective_user.id
    
    # Получаем активное голосование
    poll = db.get_active_poll()
    if not poll:
        await query.answer("❌ Нет активного голосования", show_alert=True)
        return
    
    poll_id = poll['id']
    
    # Добавляем пользователя как участника
    db.add_participant(poll_id, user_id)
    
    # Добавляем заказ
    db.add_order(poll_id, user_id, menu_item_id)
    
    # Получаем информацию о блюде
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM menu_items WHERE id = ?', (menu_item_id,))
    item = dict(cursor.fetchone())
    conn.close()
    
    await query.answer(f"✅ {item['name']} добавлено в заказ!", show_alert=True)


async def my_orders_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать мой заказ"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    poll = db.get_active_poll()
    if not poll:
        await query.edit_message_text("❌ Нет активного голосования")
        return
    
    poll_id = poll['id']
    orders = db.get_user_orders(poll_id, user_id)
    
    if not orders:
        keyboard = [[
            InlineKeyboardButton("🏠 К голосованию", callback_data="back_to_voting")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🛒 <b>Ваш заказ пуст</b>\n\n"
            "Выберите блюда из меню ресторанов",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        return
    
    order_text = "🛒 <b>Ваш заказ:</b>\n\n"
    
    total = 0
    for order in orders:
        price = order['price'] * order['quantity']
        total += price
        order_text += f"• <b>{order['name']}</b>\n"
        if order['description']:
            order_text += f"  <i>{order['description'][:50]}...</i>\n"
        order_text += f"  {order['quantity']} x {order['price']:.0f} ₽ = {price:.0f} ₽\n"
        order_text += f"  📍 {order['restaurant_name']}\n\n"
    
    order_text += f"<b>Итого: {total:.0f} ₽</b>"
    
    # Создаем кнопки для удаления блюд
    keyboard = []
    for order in orders:
        button_text = f"❌ {order['name'][:30]}"
        keyboard.append([
            InlineKeyboardButton(button_text, callback_data=f"remove_order_{order['menu_item_id']}")
        ])
    
    keyboard.append([
        InlineKeyboardButton("🗑 Очистить заказ", callback_data="clear_orders")
    ])
    keyboard.append([
        InlineKeyboardButton("🏠 К голосованию", callback_data="back_to_voting")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(order_text, parse_mode='HTML', reply_markup=reply_markup)


async def remove_order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удалить блюдо из заказа"""
    query = update.callback_query
    
    menu_item_id = int(query.data.split('_')[2])
    user_id = update.effective_user.id
    
    poll = db.get_active_poll()
    if poll:
        db.remove_order(poll['id'], user_id, menu_item_id)
        await query.answer("✅ Удалено из заказа")
        # Обновляем отображение заказа
        await my_orders_callback(update, context)
    else:
        await query.answer("❌ Ошибка", show_alert=True)


async def clear_orders_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Очистить весь заказ"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    poll = db.get_active_poll()
    if poll:
        db.clear_user_orders(poll['id'], user_id)
        
        keyboard = [[
            InlineKeyboardButton("🏠 К голосованию", callback_data="back_to_voting")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "✅ <b>Заказ очищен</b>",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    else:
        await query.answer("❌ Ошибка", show_alert=True)


# ========== Отмена ==========

async def show_menu_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список ресторанов для выбора меню"""
    query = update.callback_query
    await query.answer()
    
    restaurants = db.get_all_restaurants()
    
    if not restaurants:
        keyboard = [[
            InlineKeyboardButton("🏠 К голосованию", callback_data="back_to_voting")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("❌ Нет доступных ресторанов.", reply_markup=reply_markup)
        return
    
    keyboard = []
    for restaurant in restaurants:
        keyboard.append([
            InlineKeyboardButton(
                f"📋 {restaurant['name']}", 
                callback_data=f"menu_{restaurant['id']}"
            )
        ])
    
    # Добавляем кнопку возврата
    keyboard.append([
        InlineKeyboardButton("🏠 К голосованию", callback_data="back_to_voting")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📋 <b>Выберите ресторан для просмотра меню:</b>",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def back_to_main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вернуться на главную - показать список ресторанов для меню"""
    query = update.callback_query
    await query.answer()
    
    restaurants = db.get_all_restaurants()
    
    if not restaurants:
        keyboard = [[
            InlineKeyboardButton("🏠 К голосованию", callback_data="back_to_voting")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("❌ Нет доступных ресторанов.", reply_markup=reply_markup)
        return
    
    keyboard = []
    for restaurant in restaurants:
        keyboard.append([
            InlineKeyboardButton(
                f"📋 {restaurant['name']}", 
                callback_data=f"menu_{restaurant['id']}"
            )
        ])
    
    # Добавляем кнопку возврата
    keyboard.append([
        InlineKeyboardButton("🏠 К голосованию", callback_data="back_to_voting")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📋 <b>Выберите ресторан для просмотра меню:</b>",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def back_to_voting_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вернуться к голосованию за рестораны"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Получаем или создаем активное голосование
    poll = db.get_active_poll()
    
    if not poll:
        poll_id = db.create_poll(user_id)
    else:
        poll_id = poll['id']
    
    # Получаем список ресторанов
    restaurants = db.get_all_restaurants()
    
    if not restaurants:
        await query.edit_message_text(
            "❌ К сожалению, пока нет доступных ресторанов.\n"
            "Попросите администратора добавить рестораны."
        )
        return
    
    # Создаем клавиатуру с ресторанами
    keyboard = []
    for restaurant in restaurants:
        keyboard.append([
            InlineKeyboardButton(
                f"🍽️ {restaurant['name']}", 
                callback_data=f"vote_{restaurant['id']}"
            )
        ])
    
    # Добавляем кнопки управления
    keyboard.append([
        InlineKeyboardButton("📊 Результаты", callback_data="show_results"),
        InlineKeyboardButton("👥 Участники", callback_data="show_participants")
    ])
    keyboard.append([
        InlineKeyboardButton("📋 Меню ресторанов", callback_data="show_menu_list"),
        InlineKeyboardButton("🛒 Мой заказ", callback_data="my_orders")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Получаем текущие голоса
    user_vote = db.get_user_vote(poll_id, user_id)
    vote_text = ""
    if user_vote:
        restaurant = db.get_restaurant(user_vote)
        if restaurant:
            vote_text = f"\n\n✅ Ваш выбор: {restaurant['name']}"
    
    await query.edit_message_text(
        f"🗳️ <b>Голосование за ресторан</b>\n\n"
        f"Выберите ресторан для сегодняшнего обеда:{vote_text}",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /cancel - отменить участие"""
    user_id = update.effective_user.id
    poll = db.get_active_poll()
    
    if not poll:
        await update.message.reply_text("❌ Активного голосования нет.")
        return
    
    poll_id = poll['id']
    
    if not db.is_participant(poll_id, user_id):
        await update.message.reply_text("❌ Вы не записаны на обед.")
        return
    
    db.remove_participant(poll_id, user_id)
    await update.message.reply_text("✅ Вы отменили участие в обеде.")

