import csv
import os
import datetime
import tkinter as tk
from tkinter import simpledialog
from email_agent import LLMClient, EmailAgent


class TerminalChatBot(EmailAgent):
    def __init__(self, llm_client):
        super().__init__(llm_client)
        self.log_file = "emails.csv"
        # 确保 CSV 有表头
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(["时间", "用户输入", "AI回复"])

    def log_to_csv(self, user_input, ai_response):
        """将对话记录自动追加到 CSV"""
        with open(self.log_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_input, ai_response])

    def start_chat(self):
        # 初始化 GUI 根窗口并隐藏
        root = tk.Tk()
        root.withdraw()

        print("--- 智能终端助手已启动 (中文输入弹窗已激活) ---")
        print("--- 输入 'quit' 退出 ---")

        while True:
            # 使用弹窗输入中文 (避开 Terminal 编码问题)
            user_input = simpledialog.askstring("对话输入", "请输入你想对 AI 说的话:")

            if not user_input or user_input.lower() == 'quit':
                print("程序已退出。")
                break

            print(f"\n你: {user_input}")

            # 获取 AI 回复
            ai_response = self.llm.chat(self.system_prompt, user_input)
            print(f"AI: {ai_response}")

            # 自动保存
            self.log_to_csv(user_input, ai_response)


if __name__ == "__main__":
    # 配置信息
    API_KEY = os.getenv("OPENAI_API_KEY", "")
    BASE_URL = os.getenv("OPENAI_API_BASE", "https://api.deepseek.com").rstrip("/") + "/chat/completions"

    # 实例化并运行
    client = LLMClient(API_KEY, BASE_URL, "deepseek-chat")
    bot = TerminalChatBot(client)
    bot.start_chat()