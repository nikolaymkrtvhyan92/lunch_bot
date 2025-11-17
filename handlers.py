"""
Обработчики команд бота
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from datetime import datetime
import config

db = Database()


# ========== Хелперы для форматирования ==========

def get_category_emoji(category_name: str) -> str:
    """Получить emoji для категории меню"""
    category_lower = category_name.lower()
    
    if "холодн" in category_lower and "закуск" in category_lower:
        return "🥗"
    elif "горяч" in category_lower and "закуск" in category_lower:
        return "🔥"
    elif "салат" in category_lower:
        return "🥗"
    elif "суп" in category_lower:
        return "🍲"
    elif "шашлык" in category_lower or "гриль" in category_lower:
        return "🍖"
    elif "горяч" in category_lower and "блюд" in category_lower:
        return "🍳"
    elif "гарнир" in category_lower:
        return "🍚"
    elif "десерт" in category_lower:
        return "🍰"
    elif "напит" in category_lower:
        return "☕"
    else:
        return "🍽️"


def format_menu_beautiful(restaurant_name: str, restaurant_emoji: str, menu_items: list, mode: str = "view") -> str:
    """
    Красиво форматировать меню ресторана
    
    mode: "view" - просмотр меню, "order" - выбор блюд для заказа
    """
    if mode == "order":
        text = f"🛒 <b>Меню {restaurant_emoji} {restaurant_name}</b>\n"
        text += f"<i>Нажмите на блюдо чтобы добавить в корзину</i>\n\n"
    else:
        text = f"\n╔═══════════════════════╗\n"
        text += f"   🍽️ <b>МЕНЮ {restaurant_emoji} {restaurant_name.upper()}</b>\n"
        text += f"╚═══════════════════════╝\n\n"
    
    # Группируем по категориям
    categories = {}
    for item in menu_items:
        category = item['category'] or 'Основное меню'
        if category not in categories:
            categories[category] = []
        categories[category].append(item)
    
    # Определяем порядок категорий
    category_order = [
        "Холодные закуски",
        "Горячие закуски", 
        "Салаты",
        "Супы",
        "Шашлыки",
        "Горячие блюда",
        "Гарниры",
        "Десерты",
        "Напитки"
    ]
    
    # Сортируем категории по определенному порядку
    sorted_categories = []
    for cat in category_order:
        if cat in categories:
            sorted_categories.append((cat, categories[cat]))
    
    # Добавляем остальные категории которых нет в списке
    for cat, items in categories.items():
        if cat not in category_order:
            sorted_categories.append((cat, items))
    
    # Выводим категории
    for idx, (category, items) in enumerate(sorted_categories):
        category_emoji = get_category_emoji(category)
        
        if mode == "view":
            text += f"┌─ {category_emoji} <b>{category}</b>\n"
            text += f"│\n"
            
            for item in items:
                price = f"{int(item['price'])}" if item['price'] else "—"
                # Форматируем цену красиво
                text += f"│  • {item['name']}\n"
                text += f"│    💰 <b>{price} ₽</b>\n"
            
            text += f"└{'─' * 25}\n\n"
        else:
            text += f"{category_emoji} <b>{category}</b>\n"
            for item in items:
                price = f"{int(item['price'])}₽" if item['price'] else ""
                text += f"  • {item['name']} — {price}\n"
            text += "\n"
    
    return text


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
Привет, Команда Инкубатор! 👋

Я помогу организовать совместный обед для вашей команды! 🍽️✨

<b>🎯 Что я умею:</b>
• Голосование за рестораны
• Показываю меню с ценами  
• Веду список участников
• Отправляю напоминания
• Принимаю заказы блюд

<b>🚀 Выберите действие:</b>
"""
    
    # Создаём интерактивное меню
    keyboard = [
        [InlineKeyboardButton("🍽️ Начать голосование", callback_data="start_lunch")],
        [InlineKeyboardButton("📋 Меню ресторанов", callback_data="show_menu_list")],
        [InlineKeyboardButton("📊 Результаты", callback_data="show_results"),
         InlineKeyboardButton("👥 Участники", callback_data="show_participants")],
        [InlineKeyboardButton("🛒 Мой заказ", callback_data="show_my_order")],
    ]
    
    # Добавляем админ панель если это админ
    if user.id == int(config.ADMIN_ID):
        keyboard.append([InlineKeyboardButton("👑 Админ панель", callback_data="admin_panel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)


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
    user_id = update.effective_user.id
    
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
    
    # Находим победителя
    winner_id = None
    max_votes = 0
    
    for idx, (rest_id, rest_name, vote_count) in enumerate(votes, 1):
        if vote_count > 0:
            # Получаем emoji для ресторана
            restaurant = db.get_restaurant(rest_id)
            rest_emoji = restaurant.get('emoji', '🍽️') if restaurant else '🍽️'
            bar = "🟩" * vote_count + "⬜" * (len(participants) - vote_count) if participants else "🟩" * vote_count
            
            # Отмечаем лидера
            leader_mark = "🏆 " if vote_count >= max_votes and vote_count > 0 else ""
            result_text += f"{leader_mark}{idx}. {rest_emoji} <b>{rest_name}</b>\n   {bar} {vote_count} голос(ов)\n\n"
            
            if vote_count > max_votes:
                max_votes = vote_count
                winner_id = rest_id
    
    result_text += f"👥 Участников обеда: {len(participants)}\n"
    
    # Показываем меню ПОБЕДИТЕЛЯ голосования
    if winner_id:
        winner_restaurant = db.get_restaurant(winner_id)
        menu_items = db.get_restaurant_menu(winner_id)
        
        if winner_restaurant and menu_items:
            rest_emoji = winner_restaurant.get('emoji', '🍽️')
            
            # Используем красивое форматирование меню
            menu_text = format_menu_beautiful(
                winner_restaurant['name'],
                rest_emoji,
                menu_items,
                mode="view"
            )
            result_text += menu_text
            
            # Добавляем кнопку "Выбрать блюда"
            keyboard = [[
                InlineKeyboardButton("🛒 Выбрать блюда", callback_data=f"order_from_{winner_id}")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(result_text, parse_mode='HTML', reply_markup=reply_markup)
        else:
            await update.message.reply_text(result_text, parse_mode='HTML')
    else:
        await update.message.reply_text(result_text, parse_mode='HTML')


async def show_results_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать результаты через callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
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
    
    # Находим победителя
    winner_id = None
    max_votes = 0
    
    for idx, (rest_id, rest_name, vote_count) in enumerate(votes, 1):
        if vote_count > 0:
            # Получаем emoji для ресторана
            restaurant = db.get_restaurant(rest_id)
            rest_emoji = restaurant.get('emoji', '🍽️') if restaurant else '🍽️'
            bar = "🟩" * vote_count
            
            # Отмечаем лидера
            leader_mark = "🏆 " if vote_count > max_votes else ""
            result_text += f"{leader_mark}{idx}. {rest_emoji} <b>{rest_name}</b>: {bar} {vote_count}\n"
            
            if vote_count > max_votes:
                max_votes = vote_count
                winner_id = rest_id
    
    result_text += f"\n👥 Участников: {len(participants)}"
    
    # Показываем меню ПОБЕДИТЕЛЯ голосования
    if winner_id:
        winner_restaurant = db.get_restaurant(winner_id)
        menu_items = db.get_restaurant_menu(winner_id)
        
        if winner_restaurant and menu_items:
            rest_emoji = winner_restaurant.get('emoji', '🍽️')
            
            # Используем красивое форматирование меню
            menu_text = format_menu_beautiful(
                winner_restaurant['name'],
                rest_emoji,
                menu_items,
                mode="view"
            )
            result_text += menu_text
    
    # Добавляем кнопки (с кнопкой "Выбрать блюда")
    keyboard = []
    if winner_id:
        keyboard.append([
            InlineKeyboardButton("🛒 Выбрать блюда", callback_data=f"order_from_{winner_id}")
        ])
    keyboard.append([
        InlineKeyboardButton("👥 Участники", callback_data="show_participants"),
        InlineKeyboardButton("🏠 К голосованию", callback_data="back_to_voting")
    ])
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


# ========== Система заказа блюд ==========

async def order_from_restaurant_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'Выбрать блюда' - показывает меню для заказа"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    restaurant_id = int(query.data.split('_')[2])
    
    poll = db.get_active_poll()
    if not poll:
        await query.edit_message_text("❌ Голосование завершено.")
        return
    
    poll_id = poll['id']
    restaurant = db.get_restaurant(restaurant_id)
    menu_items = db.get_restaurant_menu(restaurant_id)
    
    if not menu_items:
        await query.edit_message_text(f"❌ В ресторане {restaurant['name']} пока нет меню.")
        return
    
    rest_emoji = restaurant.get('emoji', '🍽️')
    
    # Используем красивое форматирование меню
    text = format_menu_beautiful(
        restaurant['name'],
        rest_emoji,
        menu_items,
        mode="order"
    )
    
    # Создаём кнопки для каждого блюда
    keyboard = []
    categories = {}
    for item in menu_items:
        category = item['category'] or 'Основное меню'
        if category not in categories:
            categories[category] = []
        categories[category].append(item)
    
    # Определяем порядок категорий (такой же как в format_menu_beautiful)
    category_order = [
        "Холодные закуски", "Горячие закуски", "Салаты", "Супы",
        "Шашлыки", "Горячие блюда", "Гарниры", "Десерты", "Напитки"
    ]
    
    sorted_categories = []
    for cat in category_order:
        if cat in categories:
            sorted_categories.append((cat, categories[cat]))
    for cat, items in categories.items():
        if cat not in category_order:
            sorted_categories.append((cat, items))
    
    for category, items in sorted_categories:
        for item in items:
            price = f"{int(item['price'])}₽" if item['price'] else ""
            keyboard.append([
                InlineKeyboardButton(
                    f"➕ {item['name']} ({price})",
                    callback_data=f"add_item_{item['id']}"
                )
            ])
    
    # Добавляем кнопки управления
    keyboard.append([
        InlineKeyboardButton("🛒 Моя корзина", callback_data=f"show_cart_{restaurant_id}"),
        InlineKeyboardButton("🏠 Назад", callback_data="show_results")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)


async def add_item_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавить блюдо в корзину"""
    query = update.callback_query
    await query.answer("✅ Добавлено в корзину!")
    
    user_id = update.effective_user.id
    menu_item_id = int(query.data.split('_')[2])
    
    poll = db.get_active_poll()
    if not poll:
        await query.edit_message_text("❌ Голосование завершено.")
        return
    
    poll_id = poll['id']
    
    # Добавляем в корзину (quantity=1)
    db.add_order(poll_id, user_id, menu_item_id, quantity=1)


async def show_cart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать корзину пользователя"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    restaurant_id = int(query.data.split('_')[2])
    
    poll = db.get_active_poll()
    if not poll:
        await query.edit_message_text("❌ Голосование завершено.")
        return
    
    poll_id = poll['id']
    orders = db.get_user_orders(poll_id, user_id)
    
    if not orders:
        text = "🛒 <b>Ваша корзина пуста</b>\n\n"
        text += "Вернитесь назад и выберите блюда."
        keyboard = [[
            InlineKeyboardButton("⬅️ Вернуться к меню", callback_data=f"order_from_{restaurant_id}")
        ]]
    else:
        text = "🛒 <b>Ваша корзина:</b>\n\n"
        total = 0
        for order in orders:
            price = order['price'] * order['quantity']
            total += price
            text += f"• {order['name']} x{order['quantity']} — {int(price)}₽\n"
        
        text += f"\n💰 <b>Итого: {int(total)}₽</b>"
        
        keyboard = [
            [InlineKeyboardButton("✅ Завершить заказ", callback_data="finish_order")],
            [InlineKeyboardButton("🗑️ Очистить корзину", callback_data="clear_cart")],
            [InlineKeyboardButton("⬅️ Добавить ещё", callback_data=f"order_from_{restaurant_id}")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)


async def finish_order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Завершить заказ"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user = update.effective_user
    
    poll = db.get_active_poll()
    if not poll:
        await query.edit_message_text("❌ Голосование завершено.")
        return
    
    poll_id = poll['id']
    orders = db.get_user_orders(poll_id, user_id)
    
    if not orders:
        await query.edit_message_text("❌ Корзина пуста!")
        return
    
    text = f"✅ <b>Ваш заказ принят, {user.first_name}!</b>\n\n"
    text += "📋 <b>Вы заказали:</b>\n"
    total = 0
    for order in orders:
        price = order['price'] * order['quantity']
        total += price
        text += f"• {order['name']} x{order['quantity']} — {int(price)}₽\n"
    
    text += f"\n💰 <b>Итого: {int(total)}₽</b>\n\n"
    text += "Заказ будет отправлен менеджеру ресторана после того,\n"
    text += "как все участники сделают свой выбор.\n\n"
    text += "Используйте /myorder чтобы посмотреть свой заказ."
    
    keyboard = [[InlineKeyboardButton("🏠 На главную", callback_data="back_to_voting")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)


async def clear_cart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Очистить корзину"""
    query = update.callback_query
    await query.answer("🗑️ Корзина очищена")
    
    user_id = update.effective_user.id
    poll = db.get_active_poll()
    
    if poll:
        poll_id = poll['id']
        db.clear_user_orders(poll_id, user_id)
    
    await query.edit_message_text(
        "🗑️ Корзина очищена.\n\nИспользуйте /lunch для нового заказа.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🏠 На главную", callback_data="back_to_voting")
        ]])
    )


async def my_order_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /myorder - показать свой заказ"""
    user_id = update.effective_user.id
    poll = db.get_active_poll()
    
    if not poll:
        await update.message.reply_text("❌ Сегодня голосование еще не начато.")
        return
    
    poll_id = poll['id']
    orders = db.get_user_orders(poll_id, user_id)
    
    if not orders:
        await update.message.reply_text("🛒 У вас пока нет заказа.\n\nИспользуйте /results чтобы выбрать блюда.")
        return
    
    text = "📋 <b>Ваш текущий заказ:</b>\n\n"
    total = 0
    restaurant_name = orders[0]['restaurant_name'] if orders else ""
    
    for order in orders:
        price = order['price'] * order['quantity']
        total += price
        text += f"• {order['name']} x{order['quantity']} — {int(price)}₽\n"
    
    text += f"\n🏪 Ресторан: <b>{restaurant_name}</b>"
    text += f"\n💰 <b>Итого: {int(total)}₽</b>"
    
    await update.message.reply_text(text, parse_mode='HTML')


# ========== Обработчики для главного меню ==========

async def start_lunch_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать голосование через кнопку"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info("🔵 start_lunch_callback вызван!")
    
    query = update.callback_query
    logger.info(f"🔵 Callback data: {query.data}")
    
    await query.answer("Загружаю рестораны...")
    logger.info("🔵 Answer отправлен")
    
    try:
        # Вызываем функционал команды /lunch
        user_id = update.effective_user.id
        user = update.effective_user
        
        # Добавляем пользователя
        db.add_user(
            user_id=user.id,
            username=user.username or "",
            first_name=user.first_name or "",
            last_name=user.last_name or ""
        )
        
        # Создаём или получаем активное голосование
        today = datetime.now().strftime('%Y-%m-%d')
        poll = db.get_active_poll(today)
        
        if not poll:
            poll_id = db.create_poll(user_id, today)
            poll = db.get_poll_by_id(poll_id)
        else:
            poll_id = poll['id']
        
        # Автоматически добавляем пользователя в участники
        if not db.is_participant(poll_id, user_id):
            db.add_participant(poll_id, user_id)
        
        # Получаем список активных ресторанов
        restaurants = db.get_all_restaurants(active_only=True)
        
        if not restaurants:
            await query.edit_message_text(
                "❌ <b>Пока нет ресторанов</b>\n\n"
                "Администратор должен добавить рестораны командой:\n"
                "/add_restaurant",
                parse_mode='HTML'
            )
            return
        
        # Создаем клавиатуру с ресторанами
        keyboard = []
        for restaurant in restaurants:
            emoji = restaurant.get('emoji', '🍽️')
            keyboard.append([InlineKeyboardButton(f"{emoji} {restaurant['name']}", callback_data=f"vote_{restaurant['id']}")])
        
        # Добавляем кнопки управления
        keyboard.append([InlineKeyboardButton("👥 Участники", callback_data="show_participants"),
                         InlineKeyboardButton("📊 Результаты", callback_data="show_results")])
        keyboard.append([InlineKeyboardButton("📋 Меню ресторанов", callback_data="show_menu_list")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Получаем текущие голоса
        user_vote = db.get_user_vote(poll_id, user_id)
        vote_text = ""
        if user_vote:
            restaurant = db.get_restaurant(user_vote)
            if restaurant:
                rest_emoji = restaurant.get('emoji', '🍽️')
                vote_text = f"\n\n✅ Ваш выбор: {rest_emoji} <b>{restaurant['name']}</b>"
        
        await query.edit_message_text(
            f"🍽️ <b>Время выбирать обед!</b>\n\n"
            f"Куда пойдём сегодня? Голосуйте! 🎯{vote_text}",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    except Exception as e:
        # Если произошла ошибка - показываем пользователю
        await query.edit_message_text(
            f"❌ <b>Ошибка при загрузке</b>\n\n"
            f"Попробуйте команду /lunch\n\n"
            f"<code>{str(e)[:200]}</code>",
            parse_mode='HTML'
        )
        # Ошибка также уйдёт админу через error_handler
        raise


async def show_my_order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать заказ через кнопку"""
    query = update.callback_query
    await query.answer("Загружаю заказ...")
    
    try:
        user_id = update.effective_user.id
        poll = db.get_active_poll()
        
        if not poll:
            keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "❌ Сегодня голосование еще не начато.\n\nИспользуйте кнопку 'Начать голосование'",
                reply_markup=reply_markup
            )
            return
        
        poll_id = poll['id']
        orders = db.get_user_orders(poll_id, user_id)
        
        if not orders:
            keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "🛒 У вас пока нет заказа.\n\nСначала проголосуйте за ресторан и выберите блюда.",
                reply_markup=reply_markup
            )
            return
        
        text = "📋 <b>Ваш текущий заказ:</b>\n\n"
        total = 0
        restaurant_name = orders[0]['restaurant_name'] if orders else ""
        restaurant_id = orders[0].get('restaurant_id') if orders else None
        
        for order in orders:
            price = order['price'] * order['quantity']
            total += price
            text += f"• {order['name']} x{order['quantity']} — {int(price)}₽\n"
        
        text += f"\n🏪 Ресторан: <b>{restaurant_name}</b>"
        text += f"\n💰 <b>Итого: {int(total)}₽</b>"
        
        keyboard = [
            [InlineKeyboardButton("🗑️ Очистить корзину", callback_data="clear_cart")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
    except Exception as e:
        keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"❌ Ошибка: {str(e)[:200]}",
            reply_markup=reply_markup
        )
        raise


async def admin_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать админ панель через кнопку"""
    query = update.callback_query
    await query.answer("Загружаю админ панель...")
    
    try:
        user_id = update.effective_user.id
        
        # Проверка прав администратора
        if user_id != int(config.ADMIN_ID):
            keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("❌ У вас нет прав администратора.", reply_markup=reply_markup)
            return
        
        admin_text = """
👑 <b>Панель администратора</b>

📊 Управление системой:

<b>Рестораны:</b>
/add_restaurant - Добавить ресторан
/list_restaurants - Список ресторанов

<b>Меню:</b>
/add_menu - Добавить блюдо в меню

<b>Заказы:</b>
/send_order - Отправить заказ менеджеру

<b>Статистика:</b>
Используйте кнопки ниже
"""
        
        keyboard = [
            [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton("👥 Пользователи", callback_data="admin_users")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(admin_text, parse_mode='HTML', reply_markup=reply_markup)
    except Exception as e:
        keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"❌ Ошибка: {str(e)[:200]}", reply_markup=reply_markup)
        raise

