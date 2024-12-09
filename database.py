import sqlite3
import time

def creatDB():
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('items.db')
    cursor = conn.cursor()

    # Create a table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        orderId TEXT UNIQUE,
        item_typeId TEXT,
        tier INTEGER,
        enchantment INTEGER,
        price INTEGER,
        item_name TEXT,
        now INTEGER
    )
    ''')
    conn.commit()
    conn.close()

def submit_data(data_to_submit):
    conn = sqlite3.connect('items.db')
    cursor = conn.cursor()
    query = '''
INSERT OR REPLACE INTO items (orderId, item_typeId, tier, enchantment, price, item_name, now)
VALUES (:orderId, :item_typeId, :tier, :enchantment, :price, :item_name, :now)
'''
    cursor.execute(query,data_to_submit)
    conn.commit()
    conn.close()
def query(search_string):
    conn = sqlite3.connect('items.db')
    cursor = conn.cursor()

    # 假设search_string是一个变量，存储你要查找的子串

    # SQL查询语句，查找name字段中包含search_string的记录
    query = "SELECT * FROM items WHERE item_name LIKE ? ORDER BY tier DESC, enchantment DESC"

    # 使用模糊匹配，将search_string前后加上百分号
    cursor.execute(query, ('%' + search_string + '%',))

    # 获取所有匹配的记录
    results = cursor.fetchall()
    conn.close()
    return results
