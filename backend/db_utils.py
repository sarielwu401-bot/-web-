# 文件路径: D:\Code\MangroveProject\backend\db_utils.py
import pymysql

# 数据库配置（与你在 DBeaver 中设置的一致）
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456', 
    'database': 'mangrove_db',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    """获取数据库连接的工具函数"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except pymysql.MySQLError as e:
        print(f"数据库连接失败: {e}")
        return None