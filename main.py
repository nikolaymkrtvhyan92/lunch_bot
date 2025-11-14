"""
Главный файл телеграм бота для организации обедов
"""
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes
)

import config
from database import Database
from scheduler import LunchScheduler

# Импортируем обработчики
from handlers import (
    start_command,
    help_command,
    lunch_command,
    vote_callback,
    results_command,
    show_results_callback,
    join_command,
    participants_command,
    show_participants_callback,
    leave_callback,
    menu_command,
    show_menu_callback,
    show_category_callback,
    show_menu_list_callback,
    add_order_callback,
    my_orders_callback,
    remove_order_callback,
    clear_orders_callback,
    back_to_main_callback,
    back_to_voting_callback,
    cancel_command,
    # Новые обработчики системы заказа
    order_from_restaurant_callback,
    add_item_callback,
    show_cart_callback,
    finish_order_callback,
    clear_cart_callback,
    my_order_command,
    # Обработчики главного меню
    start_lunch_callback,
    show_my_order_callback,
    admin_panel_callback
)

from admin_handlers import (
    admin_command,
    add_restaurant_command,
    restaurant_name,
    restaurant_desc,
    restaurant_address,
    restaurant_phone,
    restaurant_emoji,
    list_restaurants_command,
    add_menu_command,
    menu_restaurant_selected,
    menu_item_name,
    menu_item_price,
    menu_item_desc,
    menu_item_category,
    admin_stats_callback,
    admin_users_callback,
    cancel_admin,
    send_order_command,
    confirm_order_callback,
    reject_order_callback,
    RESTAURANT_NAME,
    RESTAURANT_DESC,
    RESTAURANT_ADDRESS,
    RESTAURANT_PHONE,
    RESTAURANT_EMOJI,
    MENU_RESTAURANT,
    MENU_ITEM_NAME,
    MENU_ITEM_PRICE,
    MENU_ITEM_DESC,
    MENU_ITEM_CATEGORY
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Запуск бота"""
    
    # Проверяем токен
    if not config.BOT_TOKEN:
        logger.error("Токен бота не найден! Проверьте файл .env")
        return
    
    # Инициализация базы данных
    db = Database()
    logger.info("База данных инициализирована")
    
    # Создаем приложение
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # ========== Обработчики команд для пользователей ==========
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("lunch", lunch_command))
    application.add_handler(CommandHandler("results", results_command))
    application.add_handler(CommandHandler("join", join_command))
    application.add_handler(CommandHandler("participants", participants_command))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    
    # ========== Обработчики команд для администраторов ==========
    
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("list_restaurants", list_restaurants_command))
    
    # ConversationHandler для добавления ресторана
    add_restaurant_handler = ConversationHandler(
        entry_points=[CommandHandler("add_restaurant", add_restaurant_command)],
        states={
            RESTAURANT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, restaurant_name)],
            RESTAURANT_DESC: [MessageHandler(filters.TEXT, restaurant_desc)],
            RESTAURANT_ADDRESS: [MessageHandler(filters.TEXT, restaurant_address)],
            RESTAURANT_PHONE: [MessageHandler(filters.TEXT, restaurant_phone)],
            RESTAURANT_EMOJI: [MessageHandler(filters.TEXT, restaurant_emoji)],
        },
        fallbacks=[CommandHandler("cancel", cancel_admin)],
    )
    application.add_handler(add_restaurant_handler)
    
    # ConversationHandler для добавления блюда в меню
    add_menu_handler = ConversationHandler(
        entry_points=[CommandHandler("add_menu", add_menu_command)],
        states={
            MENU_RESTAURANT: [CallbackQueryHandler(menu_restaurant_selected, pattern=r'^addmenu_\d+$')],
            MENU_ITEM_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_item_name)],
            MENU_ITEM_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_item_price)],
            MENU_ITEM_DESC: [MessageHandler(filters.TEXT, menu_item_desc)],
            MENU_ITEM_CATEGORY: [MessageHandler(filters.TEXT, menu_item_category)],
        },
        fallbacks=[CommandHandler("cancel", cancel_admin)],
    )
    application.add_handler(add_menu_handler)
    
    # ========== Callback handlers ==========
    
    # Голосование
    application.add_handler(CallbackQueryHandler(vote_callback, pattern=r'^vote_\d+$'))
    application.add_handler(CallbackQueryHandler(show_results_callback, pattern=r'^show_results$'))
    
    # Участники
    application.add_handler(CallbackQueryHandler(show_participants_callback, pattern=r'^show_participants$'))
    application.add_handler(CallbackQueryHandler(leave_callback, pattern=r'^leave_lunch$'))
    
    # Меню
    application.add_handler(CallbackQueryHandler(show_menu_callback, pattern=r'^menu_\d+$'))
    application.add_handler(CallbackQueryHandler(show_category_callback, pattern=r'^category_\d+_.+$'))
    application.add_handler(CallbackQueryHandler(show_menu_list_callback, pattern=r'^show_menu_list$'))
    application.add_handler(CallbackQueryHandler(back_to_main_callback, pattern=r'^back_to_main$'))
    
    # Заказы
    application.add_handler(CallbackQueryHandler(add_order_callback, pattern=r'^order_\d+$'))
    application.add_handler(CallbackQueryHandler(my_orders_callback, pattern=r'^my_orders$'))
    application.add_handler(CallbackQueryHandler(remove_order_callback, pattern=r'^remove_order_\d+$'))
    application.add_handler(CallbackQueryHandler(clear_orders_callback, pattern=r'^clear_orders$'))
    
    # Навигация
    application.add_handler(CallbackQueryHandler(back_to_voting_callback, pattern=r'^back_to_voting$'))
    
    # Система заказа блюд
    application.add_handler(CallbackQueryHandler(order_from_restaurant_callback, pattern=r'^order_from_\d+$'))
    application.add_handler(CallbackQueryHandler(add_item_callback, pattern=r'^add_item_\d+$'))
    application.add_handler(CallbackQueryHandler(show_cart_callback, pattern=r'^show_cart_\d+$'))
    application.add_handler(CallbackQueryHandler(finish_order_callback, pattern=r'^finish_order$'))
    application.add_handler(CallbackQueryHandler(clear_cart_callback, pattern=r'^clear_cart$'))
    application.add_handler(CommandHandler("myorder", my_order_command))
    
    # Админ панель
    application.add_handler(CallbackQueryHandler(admin_stats_callback, pattern=r'^admin_stats$'))
    application.add_handler(CallbackQueryHandler(admin_users_callback, pattern=r'^admin_users$'))
    application.add_handler(CommandHandler("send_order", send_order_command))
    
    # Подтверждение/отклонение заказа менеджером
    application.add_handler(CallbackQueryHandler(confirm_order_callback, pattern=r'^confirm_order_\d+$'))
    application.add_handler(CallbackQueryHandler(reject_order_callback, pattern=r'^reject_order_\d+$'))
    
    # Главное меню (обработчики кнопок из /start)
    logger.info("🔵 Регистрируем обработчики главного меню...")
    application.add_handler(CallbackQueryHandler(start_lunch_callback, pattern=r'^start_lunch$'))
    logger.info("✅ start_lunch_callback зарегистрирован")
    application.add_handler(CallbackQueryHandler(show_my_order_callback, pattern=r'^show_my_order$'))
    application.add_handler(CallbackQueryHandler(admin_panel_callback, pattern=r'^admin_panel$'))
    logger.info("✅ Обработчики главного меню зарегистрированы")
    
    # Повторное добавление блюда
    application.add_handler(CallbackQueryHandler(menu_restaurant_selected, pattern=r'^addmenu_\d+$'))
    
    # ========== Логирование всех callback'ов ==========
    
    async def log_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Логировать все callback query для отладки"""
        if update.callback_query:
            logger.info(f"📞 CALLBACK: {update.callback_query.data} от user {update.effective_user.id}")
    
    # Добавляем в начало чтобы логировать ВСЕ callback'и
    application.add_handler(CallbackQueryHandler(log_callback), group=-1)
    
    # ========== Обработчик ошибок ==========
    
    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ошибок - отправляет админу уведомление"""
        try:
            # Получаем информацию об ошибке
            error_message = str(context.error)
            logger.error(f"Exception while handling an update: {error_message}", exc_info=context.error)
            
            # Отправляем админу
            error_text = f"⚠️ <b>ОШИБКА БОТА!</b>\n\n"
            error_text += f"<b>Ошибка:</b> {error_message[:500]}\n\n"
            
            if update:
                error_text += f"<b>User:</b> {update.effective_user.id if update.effective_user else 'Unknown'}\n"
                error_text += f"<b>Chat:</b> {update.effective_chat.id if update.effective_chat else 'Unknown'}\n"
            
            await context.bot.send_message(
                chat_id=config.ADMIN_ID,
                text=error_text,
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Error in error handler: {e}")
    
    application.add_error_handler(error_handler)
    
    # ========== Планировщик уведомлений ==========
    
    scheduler = LunchScheduler(application.bot)
    scheduler.start()
    logger.info("Планировщик уведомлений запущен")
    
    # ========== Запуск бота ==========
    
    logger.info("Бот запущен и готов к работе!")
    
    # Запускаем бота с защитой от конфликтов
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True  # Игнорировать старые обновления
    )


if __name__ == '__main__':
    main()

