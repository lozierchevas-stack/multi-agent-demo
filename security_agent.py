import time


class RateLimitMiddleware:
    """访问频率限制中间件 (滑动窗口算法)"""

    def __init__(self, max_requests: int = 3, time_window: int = 60):
        self.max_requests = max_requests  # 时间窗口内最大允许请求数
        self.time_window = time_window  # 时间窗口大小（秒）
        self.user_records = {}  # 记录用户请求时间戳

    def is_allowed(self, user_id: str = "default_user") -> tuple[bool, str]:
        current_time = time.time()

        # 1. 初始化新用户
        if user_id not in self.user_records:
            self.user_records[user_id] = [current_time]
            return True, "允许访问"

        # 2. 清理滑动窗口外的过期记录
        valid_timestamps = [
            t for t in self.user_records[user_id]
            if current_time - t < self.time_window
        ]
        self.user_records[user_id] = valid_timestamps

        # 3. 判断是否超限
        if len(valid_timestamps) >= self.max_requests:
            remaining_time = int(self.time_window - (current_time - valid_timestamps[0]))
            return False, f"请求过于频繁，请等待 {remaining_time} 秒后再试。"

        # 4. 放行并记录本次请求
        self.user_records[user_id].append(current_time)
        return True, "允许访问"


class SensitiveWordMiddleware:
    """敏感词安全验证中间件"""

    def __init__(self, block_words: list = None):
        # 默认敏感词库（实际生产中可从数据库或文件读取）
        self.block_words = block_words or ["作弊", "密码", "黑客", "暴力", "违规"]

    def check_input(self, text: str) -> tuple[bool, str]:
        """检查输入，包含敏感词则拦截"""
        for word in self.block_words:
            if word in text:
                return False, f"输入包含违规词汇: '{word}'"
        return True, "安全"

    def sanitize_output(self, text: str) -> str:
        """对输出进行脱敏替换"""
        sanitized_text = text
        for word in self.block_words:
            if word in sanitized_text:
                sanitized_text = sanitized_text.replace(word, "*" * len(word))
        return sanitized_text


class SecurityPipeline:
    """安全拦截管道，统一管理所有中间件"""

    def __init__(self):
        # 配置：每分钟最多3次请求
        self.rate_limiter = RateLimitMiddleware(max_requests=3, time_window=60)
        self.word_filter = SensitiveWordMiddleware()

    def verify_request(self, user_input: str, user_id: str = "default_user") -> tuple[bool, str]:
        """在调用大模型前执行的综合检查"""
        # 1. 检查频率
        allowed, rate_msg = self.rate_limiter.is_allowed(user_id)
        if not allowed:
            return False, f"⚠️ 限流拦截: {rate_msg}"

        # 2. 检查敏感词
        safe, filter_msg = self.word_filter.check_input(user_input)
        if not safe:
            return False, f"🚫 安全拦截: {filter_msg}"

        return True, "验证通过"

    def process_response(self, ai_response: str) -> str:
        """在返回给用户前执行的输出清洗"""
        return self.word_filter.sanitize_output(ai_response)