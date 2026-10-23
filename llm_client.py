import requests
import json
import os


class LLMClient:
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1/chat/completions",
                 model: str = "gpt-3.5-turbo"):
        """
        初始化大模型客户端 (默认使用类似 OpenAI 的接口格式，兼容大多数国产大模型)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    def chat(self, system_prompt: str, user_message: str) -> str:
        """
        发送对话请求并获取回复
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.1  # 智能体调用工具时，建议较低的温度以保证输出格式的稳定性
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            return f"Error: 模型调用失败 - {str(e)}"