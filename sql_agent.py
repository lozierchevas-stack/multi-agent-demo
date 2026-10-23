import os
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI

load_dotenv()

# 初始化数据库连接 (仅读取)
db_uri = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/agent_memory"
db = SQLDatabase.from_uri(db_uri)
llm = ChatOpenAI(model="deepseek-chat", api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_BASE"))

# 创建 Agent
agent = create_sql_agent(llm, db=db, verbose=True)

# 测试查询
response = agent.invoke("找出 sender 为 'test@example.com' 的邮件标题是什么？")
print(f"\n[AI 回答]: {response['output']}")