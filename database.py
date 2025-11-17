"""
Модуль для работы с базой данных
"""
import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple
import config


class Database:
    def __init__(self, db_name: str = config.DATABASE_NAME):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        """Получить соединение с БД"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Инициализация базы данных"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                is_admin INTEGER DEFAULT 0,
                language TEXT DEFAULT 'ru',
                access_status TEXT DEFAULT 'pending',
                requested_at TIMESTAMP,
                approved_at TIMESTAMP,
                department TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Миграция: добавление поля language
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'ru'")
        except sqlite3.OperationalError:
            pass  # Поле уже существует
        
        # Миграция: добавление полей для whitelist системы
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN access_status TEXT DEFAULT 'pending'")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN requested_at TIMESTAMP")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN approved_at TIMESTAMP")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN department TEXT")
        except sqlite3.OperationalError:
            pass
        
        # Устанавливаем админу статус "approved"
        try:
            cursor.execute("UPDATE users SET access_status = 'approved' WHERE is_admin = 1")
            conn.commit()
        except:
            pass
        
        # Таблица ресторанов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS restaurants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                address TEXT,
                phone TEXT,
                emoji TEXT DEFAULT '🍽️',
                photo_url TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Миграция: добавление полей emoji и photo_url если их нет
        try:
            cursor.execute("ALTER TABLE restaurants ADD COLUMN emoji TEXT DEFAULT '🍽️'")
        except sqlite3.OperationalError:
            pass  # Поле уже существует
        
        try:
            cursor.execute("ALTER TABLE restaurants ADD COLUMN photo_url TEXT")
        except sqlite3.OperationalError:
            pass  # Поле уже существует
        
        # Таблица меню
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                restaurant_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                category TEXT,
                is_available INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (restaurant_id) REFERENCES restaurants (id)
            )
        ''')
        
        # Таблица голосований
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS polls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_by INTEGER NOT NULL,
                date DATE NOT NULL,
                status TEXT DEFAULT 'active',
                winner_restaurant_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (user_id),
                FOREIGN KEY (winner_restaurant_id) REFERENCES restaurants (id)
            )
        ''')
        
        # Таблица голосов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                poll_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                restaurant_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (poll_id) REFERENCES polls (id),
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (restaurant_id) REFERENCES restaurants (id),
                UNIQUE(poll_id, user_id)
            )
        ''')
        
        # Таблица участников обеда
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lunch_participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                poll_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (poll_id) REFERENCES polls (id),
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                UNIQUE(poll_id, user_id)
            )
        ''')
        
        # Таблица заказов блюд
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                poll_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                menu_item_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (poll_id) REFERENCES polls (id),
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (menu_item_id) REFERENCES menu_items (id),
                UNIQUE(poll_id, user_id, menu_item_id)
            )
        ''')
        
        # Миграция: добавление полей manager_telegram_id и manager_phone
        try:
            cursor.execute("ALTER TABLE restaurants ADD COLUMN manager_telegram_id INTEGER")
        except sqlite3.OperationalError:
            pass  # Поле уже существует
        
        try:
            cursor.execute("ALTER TABLE restaurants ADD COLUMN manager_phone TEXT")
        except sqlite3.OperationalError:
            pass  # Поле уже существует
        
        conn.commit()
        conn.close()
    
    # ========== Пользователи ==========
    
    def add_user(self, user_id: int, username: str, first_name: str, last_name: str = None, language: str = 'ru'):
        """Добавить пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, language)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, language))
            conn.commit()
        finally:
            conn.close()
    
    def get_user_language(self, user_id: int) -> str:
        """Получить язык пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result['language'] if result else 'ru'
        finally:
            conn.close()
    
    def set_user_language(self, user_id: int, language: str):
        """Установить язык пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users SET language = ? WHERE user_id = ?', (language, user_id))
            conn.commit()
        finally:
            conn.close()
    
    def get_user_access_status(self, user_id: int) -> str:
        """Получить статус доступа пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT access_status FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result['access_status'] if result else 'pending'
        finally:
            conn.close()
    
    def request_access(self, user_id: int, department: str = None):
        """Запросить доступ к боту"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE users 
                SET access_status = 'pending', 
                    requested_at = CURRENT_TIMESTAMP,
                    department = ?
                WHERE user_id = ?
            ''', (department, user_id))
            conn.commit()
        finally:
            conn.close()
    
    def approve_user(self, user_id: int):
        """Одобрить пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE users 
                SET access_status = 'approved',
                    approved_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (user_id,))
            conn.commit()
        finally:
            conn.close()
    
    def reject_user(self, user_id: int):
        """Отклонить пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users SET access_status = \'rejected\' WHERE user_id = ?', (user_id,))
            conn.commit()
        finally:
            conn.close()
    
    def get_pending_users(self):
        """Получить список пользователей ожидающих одобрения"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT user_id, username, first_name, last_name, department, requested_at
                FROM users 
                WHERE access_status = 'pending'
                ORDER BY requested_at DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_all_users_list(self):
        """Получить список всех пользователей с их статусами"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT user_id, username, first_name, last_name, access_status, department, created_at
                FROM users 
                ORDER BY created_at DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def is_admin(self, user_id: int) -> bool:
        """Проверить, является ли пользователь администратором"""
        return user_id == config.ADMIN_ID or self._is_db_admin(user_id)
    
    def _is_db_admin(self, user_id: int) -> bool:
        """Проверить в БД"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT is_admin FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result and result['is_admin'] == 1
        finally:
            conn.close()
    
    def set_admin(self, user_id: int, is_admin: bool = True):
        """Установить статус администратора"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE users SET is_admin = ? WHERE user_id = ?
            ''', (1 if is_admin else 0, user_id))
            conn.commit()
        finally:
            conn.close()
    
    def get_all_users(self) -> List[dict]:
        """Получить всех пользователей"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM users')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    # ========== Рестораны ==========
    
    def add_restaurant(self, name: str, description: str = None, address: str = None, phone: str = None, 
                       emoji: str = '🍽️', photo_url: str = None, manager_telegram_id: int = None, 
                       manager_phone: str = None) -> int:
        """Добавить ресторан"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO restaurants (name, description, address, phone, emoji, photo_url, 
                                       manager_telegram_id, manager_phone)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, description, address, phone, emoji, photo_url, manager_telegram_id, manager_phone))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_restaurant(self, restaurant_id: int) -> Optional[dict]:
        """Получить ресторан по ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM restaurants WHERE id = ?', (restaurant_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
        finally:
            conn.close()
    
    def get_all_restaurants(self, active_only: bool = True) -> List[dict]:
        """Получить все рестораны"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if active_only:
                cursor.execute('SELECT * FROM restaurants WHERE is_active = 1 ORDER BY name')
            else:
                cursor.execute('SELECT * FROM restaurants ORDER BY name')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def update_restaurant(self, restaurant_id: int, name: str = None, description: str = None, 
                         address: str = None, phone: str = None):
        """Обновить данные ресторана"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            updates = []
            params = []
            if name is not None:
                updates.append('name = ?')
                params.append(name)
            if description is not None:
                updates.append('description = ?')
                params.append(description)
            if address is not None:
                updates.append('address = ?')
                params.append(address)
            if phone is not None:
                updates.append('phone = ?')
                params.append(phone)
            
            if updates:
                params.append(restaurant_id)
                cursor.execute(f'''
                    UPDATE restaurants SET {', '.join(updates)} WHERE id = ?
                ''', params)
                conn.commit()
        finally:
            conn.close()
    
    def delete_restaurant(self, restaurant_id: int):
        """Удалить ресторан (деактивировать)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE restaurants SET is_active = 0 WHERE id = ?', (restaurant_id,))
            conn.commit()
        finally:
            conn.close()
    
    # ========== Меню ==========
    
    def add_menu_item(self, restaurant_id: int, name: str, price: float, 
                     description: str = None, category: str = None) -> int:
        """Добавить блюдо в меню"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO menu_items (restaurant_id, name, description, price, category)
                VALUES (?, ?, ?, ?, ?)
            ''', (restaurant_id, name, description, price, category))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_restaurant_menu(self, restaurant_id: int, available_only: bool = True) -> List[dict]:
        """Получить меню ресторана"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if available_only:
                cursor.execute('''
                    SELECT * FROM menu_items 
                    WHERE restaurant_id = ? AND is_available = 1 
                    ORDER BY category, name
                ''', (restaurant_id,))
            else:
                cursor.execute('''
                    SELECT * FROM menu_items 
                    WHERE restaurant_id = ? 
                    ORDER BY category, name
                ''', (restaurant_id,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def update_menu_item(self, item_id: int, name: str = None, description: str = None,
                        price: float = None, category: str = None, is_available: bool = None):
        """Обновить блюдо в меню"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            updates = []
            params = []
            if name is not None:
                updates.append('name = ?')
                params.append(name)
            if description is not None:
                updates.append('description = ?')
                params.append(description)
            if price is not None:
                updates.append('price = ?')
                params.append(price)
            if category is not None:
                updates.append('category = ?')
                params.append(category)
            if is_available is not None:
                updates.append('is_available = ?')
                params.append(1 if is_available else 0)
            
            if updates:
                params.append(item_id)
                cursor.execute(f'''
                    UPDATE menu_items SET {', '.join(updates)} WHERE id = ?
                ''', params)
                conn.commit()
        finally:
            conn.close()
    
    def delete_menu_item(self, item_id: int):
        """Удалить блюдо из меню"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM menu_items WHERE id = ?', (item_id,))
            conn.commit()
        finally:
            conn.close()
    
    # ========== Голосования ==========
    
    def create_poll(self, user_id: int, date: str = None) -> int:
        """Создать голосование"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO polls (created_by, date, status)
                VALUES (?, ?, 'active')
            ''', (user_id, date))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_active_poll(self, date: str = None) -> Optional[dict]:
        """Получить активное голосование"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT * FROM polls 
                WHERE date = ? AND status = 'active'
                ORDER BY created_at DESC
                LIMIT 1
            ''', (date,))
            result = cursor.fetchone()
            return dict(result) if result else None
        finally:
            conn.close()
    
    def get_poll_by_id(self, poll_id: int) -> Optional[dict]:
        """Получить голосование по ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM polls WHERE id = ?', (poll_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
        finally:
            conn.close()
    
    def add_vote(self, poll_id: int, user_id: int, restaurant_id: int) -> bool:
        """Добавить голос"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO votes (poll_id, user_id, restaurant_id)
                VALUES (?, ?, ?)
            ''', (poll_id, user_id, restaurant_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding vote: {e}")
            return False
        finally:
            conn.close()
    
    def get_poll_votes(self, poll_id: int) -> List[Tuple[int, str, int]]:
        """Получить результаты голосования (restaurant_id, restaurant_name, vote_count)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT r.id, r.name, COUNT(v.id) as votes
                FROM restaurants r
                LEFT JOIN votes v ON r.id = v.restaurant_id AND v.poll_id = ?
                WHERE r.is_active = 1
                GROUP BY r.id, r.name
                ORDER BY votes DESC, r.name
            ''', (poll_id,))
            return [(row['id'], row['name'], row['votes']) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def close_poll(self, poll_id: int, winner_restaurant_id: int = None):
        """Закрыть голосование"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE polls 
                SET status = 'closed', winner_restaurant_id = ?, closed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (winner_restaurant_id, poll_id))
            conn.commit()
        finally:
            conn.close()
    
    def get_user_vote(self, poll_id: int, user_id: int) -> Optional[int]:
        """Получить голос пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT restaurant_id FROM votes 
                WHERE poll_id = ? AND user_id = ?
            ''', (poll_id, user_id))
            result = cursor.fetchone()
            return result['restaurant_id'] if result else None
        finally:
            conn.close()
    
    # ========== Участники обеда ==========
    
    def add_participant(self, poll_id: int, user_id: int) -> bool:
        """Добавить участника обеда"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO lunch_participants (poll_id, user_id)
                VALUES (?, ?)
            ''', (poll_id, user_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def remove_participant(self, poll_id: int, user_id: int) -> bool:
        """Удалить участника обеда"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                DELETE FROM lunch_participants
                WHERE poll_id = ? AND user_id = ?
            ''', (poll_id, user_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def get_participants(self, poll_id: int) -> List[dict]:
        """Получить список участников обеда"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT u.* FROM users u
                JOIN lunch_participants lp ON u.user_id = lp.user_id
                WHERE lp.poll_id = ?
                ORDER BY u.first_name
            ''', (poll_id,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def is_participant(self, poll_id: int, user_id: int) -> bool:
        """Проверить, является ли пользователь участником обеда"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT 1 FROM lunch_participants
                WHERE poll_id = ? AND user_id = ?
            ''', (poll_id, user_id))
            return cursor.fetchone() is not None
        finally:
            conn.close()
    
    # ========== Заказы блюд ==========
    
    def add_order(self, poll_id: int, user_id: int, menu_item_id: int, quantity: int = 1) -> bool:
        """Добавить заказ блюда"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO user_orders (poll_id, user_id, menu_item_id, quantity)
                VALUES (?, ?, ?, ?)
            ''', (poll_id, user_id, menu_item_id, quantity))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding order: {e}")
            return False
        finally:
            conn.close()
    
    def remove_order(self, poll_id: int, user_id: int, menu_item_id: int) -> bool:
        """Удалить заказ блюда"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                DELETE FROM user_orders
                WHERE poll_id = ? AND user_id = ? AND menu_item_id = ?
            ''', (poll_id, user_id, menu_item_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def get_user_orders(self, poll_id: int, user_id: int) -> List[dict]:
        """Получить заказы пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT uo.*, mi.name, mi.price, mi.description, mi.category, r.name as restaurant_name
                FROM user_orders uo
                JOIN menu_items mi ON uo.menu_item_id = mi.id
                JOIN restaurants r ON mi.restaurant_id = r.id
                WHERE uo.poll_id = ? AND uo.user_id = ?
                ORDER BY mi.category, mi.name
            ''', (poll_id, user_id))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_all_orders(self, poll_id: int) -> List[dict]:
        """Получить все заказы для голосования"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT uo.*, u.first_name, u.last_name, u.username,
                       mi.name as dish_name, mi.price, mi.category,
                       r.name as restaurant_name
                FROM user_orders uo
                JOIN users u ON uo.user_id = u.user_id
                JOIN menu_items mi ON uo.menu_item_id = mi.id
                JOIN restaurants r ON mi.restaurant_id = r.id
                WHERE uo.poll_id = ?
                ORDER BY u.first_name, mi.category, mi.name
            ''', (poll_id,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def clear_user_orders(self, poll_id: int, user_id: int) -> bool:
        """Очистить все заказы пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                DELETE FROM user_orders
                WHERE poll_id = ? AND user_id = ?
            ''', (poll_id, user_id))
            conn.commit()
            return True
        finally:
            conn.close()
    
    def get_order_summary(self, poll_id: int) -> List[dict]:
        """Получить сводку по заказам (блюдо -> количество)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT mi.name, mi.price, r.name as restaurant_name,
                       SUM(uo.quantity) as total_quantity,
                       COUNT(DISTINCT uo.user_id) as user_count
                FROM user_orders uo
                JOIN menu_items mi ON uo.menu_item_id = mi.id
                JOIN restaurants r ON mi.restaurant_id = r.id
                WHERE uo.poll_id = ?
                GROUP BY mi.id, mi.name, mi.price, r.name
                ORDER BY r.name, mi.name
            ''', (poll_id,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

