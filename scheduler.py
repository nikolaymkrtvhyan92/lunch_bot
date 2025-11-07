"""
Планировщик уведомлений
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from database import Database
import config
import logging

logger = logging.getLogger(__name__)

db = Database()


class LunchScheduler:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)
    
    def start(self):
        """Запустить планировщик"""
        # Парсим время обеда
        try:
            hour, minute = map(int, config.LUNCH_TIME.split(':'))
        except:
            logger.error(f"Неверный формат времени: {config.LUNCH_TIME}")
            hour, minute = 12, 0
        
        # Добавляем задачу на отправку уведомлений
        self.scheduler.add_job(
            self.send_lunch_notification,
            trigger=CronTrigger(hour=hour, minute=minute, timezone=config.TIMEZONE),
            id='lunch_notification',
            replace_existing=True
        )
        
        # Добавляем задачу на подведение итогов (за 30 минут до обеда)
        reminder_minute = (minute - 30) % 60
        reminder_hour = hour if minute >= 30 else hour - 1
        
        self.scheduler.add_job(
            self.send_voting_reminder,
            trigger=CronTrigger(hour=reminder_hour, minute=reminder_minute, timezone=config.TIMEZONE),
            id='voting_reminder',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info(f"Планировщик запущен. Уведомления в {hour:02d}:{minute:02d}")
    
    async def send_lunch_notification(self):
        """Отправить уведомление о времени обеда"""
        try:
            # Получаем активное голосование
            poll = db.get_active_poll()
            
            if not poll:
                # Если голосования нет, отправляем всем напоминание
                users = db.get_all_users()
                
                message = (
                    "🔔 <b>Время обеда!</b>\n\n"
                    "Сегодня еще не начато голосование за ресторан.\n"
                    "Используйте /lunch чтобы начать голосование."
                )
                
                for user in users:
                    try:
                        await self.bot.send_message(
                            chat_id=user['user_id'],
                            text=message,
                            parse_mode='HTML'
                        )
                    except Exception as e:
                        logger.error(f"Не удалось отправить уведомление пользователю {user['user_id']}: {e}")
                
                return
            
            # Получаем результаты голосования
            poll_id = poll['id']
            votes = db.get_poll_votes(poll_id)
            participants = db.get_participants(poll_id)
            
            if not votes or all(v[2] == 0 for v in votes):
                message = (
                    "🔔 <b>Время обеда!</b>\n\n"
                    "К сожалению, никто не проголосовал за ресторан 😢\n"
                    "Используйте /lunch чтобы проголосовать."
                )
            else:
                # Определяем победителя
                winner = votes[0]
                winner_id, winner_name, winner_votes = winner
                
                # Закрываем голосование
                db.close_poll(poll_id, winner_id)
                
                message = (
                    "🔔 <b>Время обеда!</b>\n\n"
                    f"🏆 Победитель голосования: <b>{winner_name}</b>\n"
                    f"📊 Голосов: {winner_votes}\n"
                    f"👥 Участников: {len(participants)}\n\n"
                )
                
                if participants:
                    message += "<b>Идут на обед:</b>\n"
                    for participant in participants[:10]:  # Показываем первых 10
                        name = participant['first_name']
                        message += f"• {name}\n"
                    
                    if len(participants) > 10:
                        message += f"... и еще {len(participants) - 10} человек\n"
                
                message += "\nПриятного аппетита! 🍽️"
            
            # Отправляем уведомление всем участникам
            if participants:
                keyboard = [[
                    InlineKeyboardButton("📋 Меню ресторана", callback_data=f"menu_{winner_id}")
                ]] if votes and votes[0][2] > 0 else []
                reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
                
                for participant in participants:
                    try:
                        await self.bot.send_message(
                            chat_id=participant['user_id'],
                            text=message,
                            parse_mode='HTML',
                            reply_markup=reply_markup
                        )
                    except Exception as e:
                        logger.error(f"Не удалось отправить уведомление пользователю {participant['user_id']}: {e}")
            else:
                # Если нет участников, отправляем всем пользователям
                users = db.get_all_users()
                for user in users:
                    try:
                        await self.bot.send_message(
                            chat_id=user['user_id'],
                            text=message,
                            parse_mode='HTML'
                        )
                    except Exception as e:
                        logger.error(f"Не удалось отправить уведомление пользователю {user['user_id']}: {e}")
        
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления о обеде: {e}")
    
    async def send_voting_reminder(self):
        """Отправить напоминание о голосовании"""
        try:
            poll = db.get_active_poll()
            
            if not poll:
                return  # Если голосования нет, не напоминаем
            
            poll_id = poll['id']
            votes = db.get_poll_votes(poll_id)
            users = db.get_all_users()
            
            # Получаем список тех, кто еще не проголосовал
            voted_users = set()
            for _, _, _ in votes:
                # Получаем пользователей, которые проголосовали
                pass  # Здесь можно добавить логику
            
            message = (
                "⏰ <b>Напоминание!</b>\n\n"
                "Через 30 минут обед! 🍽️\n"
                "Не забудьте проголосовать за ресторан: /lunch\n"
                "И записаться на обед: /join"
            )
            
            # Отправляем напоминание всем пользователям
            for user in users:
                try:
                    await self.bot.send_message(
                        chat_id=user['user_id'],
                        text=message,
                        parse_mode='HTML'
                    )
                except Exception as e:
                    logger.error(f"Не удалось отправить напоминание пользователю {user['user_id']}: {e}")
        
        except Exception as e:
            logger.error(f"Ошибка при отправке напоминания: {e}")
    
    def stop(self):
        """Остановить планировщик"""
        self.scheduler.shutdown()
        logger.info("Планировщик остановлен")

