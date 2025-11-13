"""
Скрипт миграции: добавление уникальных emoji для существующих ресторанов
"""
from database import Database

# Маппинг имён ресторанов на emoji
RESTAURANT_EMOJI = {
    'ани': '🥘',  # Армянская кухня
    'ani': '🥘',
    'бургерная': '🍔',
    'burger': '🍔',
    'итальянская': '🍝',
    'italian': '🍝',
    'суши': '🍣',
    'sushi': '🍣',
    'японская': '🍱',
    'japanese': '🍱',
    'китайская': '🥡',
    'chinese': '🥡',
    'пицца': '🍕',
    'pizza': '🍕',
    'мексиканская': '🌮',
    'mexican': '🌮',
    'грузинская': '🫓',
    'georgian': '🫓',
    'стейк': '🥩',
    'steak': '🥩',
    'кафе': '☕',
    'cafe': '☕',
    'десерт': '🍰',
    'dessert': '🍰',
}

def get_emoji_for_restaurant(name: str) -> str:
    """Определить emoji по названию ресторана"""
    name_lower = name.lower()
    
    # Ищем ключевые слова в названии
    for keyword, emoji in RESTAURANT_EMOJI.items():
        if keyword in name_lower:
            return emoji
    
    # По умолчанию
    return '🍽️'

def migrate_emoji():
    """Обновить emoji для всех существующих ресторанов"""
    db = Database()
    restaurants = db.get_all_restaurants()
    
    print(f"📊 Найдено ресторанов: {len(restaurants)}")
    print("=" * 50)
    
    for restaurant in restaurants:
        rest_id = restaurant['id']
        name = restaurant['name']
        current_emoji = restaurant.get('emoji', '🍽️')
        
        # Определяем подходящий emoji
        new_emoji = get_emoji_for_restaurant(name)
        
        # Обновляем только если emoji по умолчанию
        if current_emoji == '🍽️' or current_emoji is None:
            conn = db.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    UPDATE restaurants 
                    SET emoji = ? 
                    WHERE id = ?
                ''', (new_emoji, rest_id))
                conn.commit()
                print(f"✅ {name}: {current_emoji} → {new_emoji}")
            except Exception as e:
                print(f"❌ Ошибка при обновлении {name}: {e}")
            finally:
                conn.close()
        else:
            print(f"⏭️  {name}: {current_emoji} (не изменено)")
    
    print("=" * 50)
    print("✅ Миграция завершена!")

if __name__ == '__main__':
    migrate_emoji()

