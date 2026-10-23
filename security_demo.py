import time
import requests
import json


# ==========================================
# 1. 限制模型访问次数中间件 (Rate Limiter)
# ==========================================
class RateLimitMiddleware:
    """访问频率限制中间件 (滑动窗口算法)"""

    def __init__(self, max_requests: int = 3, time_window: int = 60):
        self.max_requests = max_requests  # 时间窗口内最大允许请求数
        self.time_window = time_window  # 时间窗口大小（秒）
        self.user_records = {}  # 记录用户请求时间戳

    def is_allowed(self, user_id: str = "default_user") -> tuple[bool, str]:
        current_time = time.time()

        if user_id not in self.user_records:
            self.user_records[user_id] = [current_time]
            return True, "允许访问"

        # 清理滑动窗口外的过期记录
        valid_timestamps = [
            t for t in self.user_records[user_id]
            if current_time - t < self.time_window
        ]
        self.user_records[user_id] = valid_timestamps

        # 判断是否超限
        if len(valid_timestamps) >= self.max_requests:
            remaining_time = int(self.time_window - (current_time - valid_timestamps[0]))
            return False, f"请求过于频繁，请等待 {remaining_time} 秒后再试。"

        self.user_records[user_id].append(current_time)
        return True, "允许访问"


# ==========================================
# 2. 敏感词验证中间件 (Content Filter)
# ==========================================
class SensitiveWordMiddleware:
    """敏感词安全验证中间件"""

    def __init__(self, block_words: list = None):
        self.block_words = block_words or ["作弊", "密码", "黑客", "暴力"]

    def check_input(self, text: str) -> tuple[bool, str]:
        """检查输入，包含敏感词则拦截"""
        for word in self.block_words:
            if word in text:
                return False, f"输入包含违规词汇: '{word}'"
        return True, "安全"


# ==========================================
# 3. 核心大模型客户端 (基础类)
# ==========================================
class LLMClient:
    def __init__(self, api_key: str = "mock_key", base_url: str = "", model: str = "mock-model"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    def chat(self, user_message: str) -> str:
        # 这里为了方便你无密钥直接运行测试，使用了模拟回复
        return f"【AI的回答】: 收到您的请求 '{user_message}'，已成功处理。"


# ==========================================
# 4. 组装智能体安全系统 (Agent Pipeline)
# ==========================================
class SecureEmailAgent:
    def __init__(self):
        self.llm = LLMClient()
        # 初始化中间件：限制每 60 秒最多 3 次请求
        self.rate_limiter = RateLimitMiddleware(max_requests=3, time_window=60)
        self.word_filter = SensitiveWordMiddleware()

    def run(self, user_input: str, user_id: str = "user_001"):
        print(f"\n[用户输入]: {user_input}")

        # 验证 1：敏感词验证中间件
        is_safe, filter_msg = self.word_filter.check_input(user_input)
        if not is_safe:
            print(f"❌ 敏感词中间体拦截: {filter_msg}")
            return

        # 验证 2：限流中间件
        allowed, rate_msg = self.rate_limiter.is_allowed(user_id)
        if not allowed:
            print(f"⚠️ 限流中间体拦截: {rate_msg}")
            return

        # 验证通过，调用大模型
        response = self.llm.chat(user_input)
        print(response)


# ==========================================
# 5. 测试用例与效果输出
# ==========================================
if __name__ == "__main__":
    agent = SecureEmailAgent()

    print("=== 阶段一：敏感词验证测试 ===")
    agent.run("今天天气怎么样？")
    agent.run("教我怎么当一个黑客？")  # 包含敏感词“黑客”

    print("\n=== 阶段二：限制访问次数测试 ===")
    agent.run("吃饭了吗")
    agent.run("吃饭了吗")
    agent.run("吃饭了吗")
    agent.run("吃饭了吗")  # 超过每分钟3次限制