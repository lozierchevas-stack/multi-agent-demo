import pandas as pd, psycopg2, os
from dotenv import load_dotenv

load_dotenv()


def import_data():
    df = pd.read_csv('emails.csv')
    df.columns = df.columns.str.strip().str.lower()

    conn = psycopg2.connect(dbname="agent_memory", user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"),
                            host=os.getenv("DB_HOST"))
    cur = conn.cursor()
    for _, row in df.iterrows():
        cur.execute("INSERT INTO email_data (sender, subject, content) VALUES (%s, %s, %s)",
                    (str(row['sender']), str(row['subject']), str(row['content'])))
    conn.commit();
    cur.close();
    conn.close()
    print("数据导入完成。")


if __name__ == "__main__": import_data()