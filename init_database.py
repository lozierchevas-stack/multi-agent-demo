import psycopg2, os
from dotenv import load_dotenv

load_dotenv()


def init_db():
    # 1. 确保数据库已存在（如果报错，请手动在 pgAdmin 中创建 agent_memory 库）
    conn = psycopg2.connect(dbname="postgres", user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"),
                            host=os.getenv("DB_HOST"))
    conn.autocommit = True
    cur = conn.cursor()
    # 这一行只在库不存在时才跑，如果已经有了就不管它
    try:
        cur.execute("CREATE DATABASE agent_memory;")
    except:
        pass
    cur.close();
    conn.close()

    # 2. 建表
    conn = psycopg2.connect(dbname="agent_memory", user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"),
                            host=os.getenv("DB_HOST"))
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS email_data;")  # 每次重置表，保证数据干净
    cur.execute("CREATE TABLE email_data (id SERIAL PRIMARY KEY, sender TEXT, subject TEXT, content TEXT);")
    conn.commit();
    cur.close();
    conn.close()
    print("数据库和表初始化完成。")


if __name__ == "__main__": init_db()