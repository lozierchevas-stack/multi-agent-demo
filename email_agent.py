import csv
import os
import json
import smtplib
import datetime
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header


# ==========================================
# 1. 大模型客户端
# ==========================================
class LLMClient:
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    def chat(self, system_prompt: str, user_message: str) -> str:
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.1
        }
        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"Error: 模型调用失败 - {str(e)}"


# ==========================================
# 2. 邮件工具
# ==========================================
def send_email_tool(to_email: str, subject: str, content: str) -> str:
    SMTP_SERVER = "smtp.qq.com"
    SMTP_PORT = 465
    SENDER_EMAIL = "xxx"
    SENDER_PASSWORD = "xxx"

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = Header(subject, 'utf-8')
        msg.attach(MIMEText(content, 'plain', 'utf-8'))

        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, [to_email], msg.as_string())
        server.quit()
        return "成功"
    except Exception as e:
        return f"失败: {str(e)}"


# ==========================================
# 3. 智能体与自动记录系统
# ==========================================
class EmailAgent:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.csv_file = "email_logs.csv"
        self.system_prompt = f"""
        你是一个得力的私人助理。当前系统真实时间是：{datetime.datetime.now().strftime("%Y年%m月%d日")}。
        如果你判断用户的意图是发送邮件，严格输出 JSON：
        {{"action": "send_email", "to_email": "邮箱", "subject": "主题", "content": "内容"}}
        """
        # 初始化 CSV 日志文件
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(["时间", "收件人", "主题", "内容", "状态"])

    def log_to_csv(self, to_email, subject, content, result):
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), to_email, subject, content, result])

    def run(self, user_input: str):
        print(f"\nUser: {user_input}")
        response = self.llm.chat(self.system_prompt, user_input)
        try:
            # 清理可能的 Markdown 格式
            clean_json = response.replace("```json", "").replace("```", "").strip()
            action_request = json.loads(clean_json)

            if action_request.get("action") == "send_email":
                result = send_email_tool(
                    action_request.get("to_email"),
                    action_request.get("subject"),
                    action_request.get("content")
                )
                self.log_to_csv(action_request.get("to_email"), action_request.get("subject"),
                                action_request.get("content"), result)
                print(f"Agent 执行结果: {result} (已存入 CSV)")
        except Exception as e:
            print(f"Agent 回复: {response}")


# ==========================================
# 4. 主程序入口
# ==========================================
if __name__ == "__main__":
    API_KEY = os.getenv("OPENAI_API_KEY", "")
    BASE_URL = os.getenv("OPENAI_API_BASE", "https://api.deepseek.com").rstrip("/") + "/chat/completions"

    agent = EmailAgent(LLMClient(API_KEY, BASE_URL, "deepseek-chat"))
    agent.run("")