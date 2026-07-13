# app/database.py - 数据库模块
# 负责创建数据库连接和初始化所有数据表
import sqlite3
from datetime import datetime

# 数据库文件路径（项目根目录下会生成 lyaitest.db 文件）
DB_PATH = "lyaitest.db"

def get_connection():
    """
    获取数据库连接
    
    每次调用都会创建一个新的数据库连接，使用完后需要手动关闭。
    row_factory = sqlite3.Row 让查询结果可以通过列名访问（如 row["id"]）
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    初始化数据库：创建所有表
    
    如果表已存在，不会重复创建（IF NOT EXISTS）。
    包含三张表：sessions（会话）、messages（消息）、reports（测试报告）
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. 会话表：存储所有会话的基本信息
    # - session_id: 会话唯一标识（主键）
    # - name: 会话名称（用户创建时自定义）
    # - created_at: 创建时间（ISO格式字符串）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    # 2. 消息表：存储每个会话中的聊天消息
    # - id: 自增主键
    # - session_id: 关联到 sessions 表
    # - role: "user" 或 "assistant"
    # - content: 消息内容
    # - created_at: 消息时间
    # - FOREIGN KEY: 保证 session_id 必须存在于 sessions 表中
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
    """)
    
    # 3. 测试报告表：存储每次测试的执行结果
    # - id: 报告唯一标识（8位随机字符串）
    # - session_id: 关联到哪个会话
    # - test_type: "api" 或 "web"
    # - url: 测试的URL
    # - status_code: HTTP状态码（如 200、404）
    # - response_time: 响应时间（秒）
    # - title: 页面标题（仅Web测试有）
    # - screenshot: 截图文件路径（仅Web测试有）
    # - error: 错误信息（测试失败时记录）
    # - created_at: 报告生成时间
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            test_type TEXT NOT NULL,
            url TEXT NOT NULL,
            status_code INTEGER,
            response_time REAL,
            title TEXT,
            screenshot TEXT,
            error TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成")