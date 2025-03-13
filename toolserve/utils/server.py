import os
import sqlite3
from utils.tool import now

# 全局数据对象，用于存储操作结果
data = {
    'data': [],      # 存储查询结果
    'time': now(),   # 当前时间
    'message': ''    # 操作消息
}

# 数据库表名
TABLE_NAME = 'app_package'

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server.db')

def execute_sql(sql, params=None, fetch=False):
    """
    执行 SQL 语句的通用函数
    :param sql: 要执行的 SQL 语句
    :param params: SQL 参数（可选）
    :param fetch: 是否需要获取查询结果（默认为 False）
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row  # 将结果转换为字典
            cursor = conn.cursor()
            cursor.execute(sql, params or ())  # 执行 SQL
            if fetch:
                data['data'] = [dict(row) for row in cursor.fetchall()]  # 获取查询结果
            conn.commit()  # 提交事务
    except Exception as e:
        print(f"数据库操作失败: {e}")

def select_records(table, query=None):
    """
    查询数据
    :param table: 表名
    :param query: 查询条件（可选）
    """
    columns = ['id', 'app_name', 'notes', 'status']  # 查询的列
    sql = f"SELECT {', '.join(columns)} FROM {table}"
    params = []
    if query:
        conditions = [f"{key} = ?" for key in query.keys()]  # 动态生成查询条件
        sql += " WHERE " + " AND ".join(conditions)
        params = list(query.values())
    execute_sql(sql, params, fetch=True)

def insert_record(table, record):
    """
    插入数据
    :param table: 表名
    :param record: 要插入的数据（字典形式）
    """
    columns = ', '.join(record.keys())  # 列名
    placeholders = ', '.join(['?'] * len(record))  # 占位符
    sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    execute_sql(sql, list(record.values()))

def update_record(table, record):
    """
    更新数据
    :param table: 表名
    :param record: 要更新的数据（字典形式，包含 id）
    """
    if record and 'id' in record:
        record_id = record.pop('id')  # 移除 id，避免更新 id 字段
        set_clause = ', '.join([f"{key} = ?" for key in record.keys()])  # 动态生成 SET 子句
        sql = f"UPDATE {table} SET {set_clause} WHERE id = ?"
        params = list(record.values()) + [record_id]  # 参数列表
        execute_sql(sql, params)

def soft_delete_record(table, record_id):
    """
    软删除数据（将状态设置为 0）
    :param table: 表名
    :param record_id: 要删除的记录 ID
    """
    if record_id:
        sql = f"UPDATE {table} SET status = 0 WHERE id = ?"
        execute_sql(sql, (record_id,))

def server(func):
    """
    服务器请求处理装饰器
    :param func: 被装饰的函数
    """
    def wrapper(*args, **kwargs):
        data['message'] = args[0]  # 设置操作消息
        data['data'] = []  # 清空数据

        # 使用字典映射代替多个 if-elif
        actions = {
            'POST': lambda: insert_record(TABLE_NAME, args[1]),
            'GET': lambda: select_records(TABLE_NAME, args[1]),
            'PUT': lambda: update_record(TABLE_NAME, args[1]),
            'DELETE': lambda: soft_delete_record(TABLE_NAME, args[1])
        }

        # 执行对应的操作
        action = actions.get(args[0])
        if action:
            action()
        else:
            print('请求错误')

        return func(*args, **kwargs)
    return wrapper