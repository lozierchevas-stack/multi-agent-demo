# Multi-Agent Demo

基于 LLM 的多智能体演示项目,包含邮件智能体、SQL 查询智能体、终端聊天助手,以及安全中间件(限流、敏感词过滤)。

## 项目结构

| 文件 | 说明 |
| --- | --- |
| `llm_client.py` | 通用大模型客户端,兼容 OpenAI 格式接口(requests 实现) |
| `email_agent.py` | 邮件智能体:LLM 解析邮件指令 → SMTP 发送 → CSV 记录 |
| `terminal_chat.py` | 终端聊天助手(Tkinter 中文输入弹窗,对话自动存入 CSV) |
| `media_agent.py` | 模型访问限流中间件(支持多模型多策略) |
| `security_agent.py` | 安全中间件:滑动窗口限流 + 敏感词过滤 |
| `security_demo.py` | 安全系统演示,**无需 API 密钥**即可运行(内置模拟 LLM) |
| `sql_agent.py` | LangChain SQL Agent,用自然语言查询 PostgreSQL |
| `init_database.py` | 初始化 `agent_memory` 数据库和 `email_data` 表 |
| `import_data.py` | 导入测试数据到数据库 |

## 环境配置

1. 复制 `.env.example` 为 `.env`,填入你的密钥:

```bash
cp .env.example .env
```

2. 安装依赖:

```bash
pip install -r requirements.txt
```

3. 需要 PostgreSQL 作为记忆数据库(仅 `sql_agent.py` 需要):

```bash
python init_database.py
cp emails_sample.csv emails.csv   # 用样例数据生成 emails.csv(运行日志,不入库)
python import_data.py
```

## 快速开始

```bash
# 无需密钥的安全中间件演示
python security_demo.py

# 终端聊天助手(需要配置 OPENAI_API_KEY)
python terminal_chat.py

# 自然语言查询数据库
python sql_agent.py
```

## 环境变量

| 变量 | 说明 |
| --- | --- |
| `OPENAI_API_KEY` | LLM API 密钥(兼容 OpenAI 格式的服务均可) |
| `OPENAI_API_BASE` | API 基础地址,例如 `https://api.deepseek.com` |
| `DB_USER` / `DB_PASSWORD` / `DB_HOST` | PostgreSQL 连接信息 |

> ⚠️ 请勿将 `.env` 文件提交到仓库。
