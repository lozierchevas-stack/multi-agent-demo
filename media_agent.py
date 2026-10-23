import time
from collections import defaultdict
from functools import wraps
from typing import Callable, Dict, Optional, Tuple, Any


class RateLimitMiddleware:
    """
    限制模型访问次数的中间件智能体

    功能：
    1. 基于时间窗口的访问频率限制
    2. 支持不同模型的不同限制策略
    3. 提供访问统计信息
    """

    def __init__(self):
        # 存储每个模型的访问记录: {model_name: [(timestamp, user_id), ...]}
        self.access_records: Dict[str, list] = defaultdict(list)
        # 存储每个模型的限制策略: {model_name: (max_requests, time_window)}
        self.rate_limits: Dict[str, Tuple[int, int]] = {}
        # 存储每个用户的访问统计: {user_id: {model_name: count}}
        self.user_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def set_rate_limit(self, model_name: str, max_requests: int, time_window: int):
        """
        设置模型的访问限制

        参数:
            model_name: 模型名称
            max_requests: 时间窗口内允许的最大请求数
            time_window: 时间窗口(秒)
        """
        self.rate_limits[model_name] = (max_requests, time_window)

    def check_rate_limit(self, model_name: str, user_id: str) -> bool:
        """
        检查用户访问是否超过限制

        参数:
            model_name: 模型名称
            user_id: 用户ID

        返回:
            bool: True表示允许访问，False表示超过限制
        """
        if model_name not in self.rate_limits:
            # 如果没有设置限制，默认允许
            return True

        max_requests, time_window = self.rate_limits[model_name]
        current_time = time.time()

        # 获取该模型的访问记录
        records = self.access_records[model_name]

        # 移除时间窗口外的记录
        self.access_records[model_name] = [
            (timestamp, uid) for timestamp, uid in records
            if current_time - timestamp < time_window
        ]

        # 统计当前用户在时间窗口内的访问次数
        user_requests = sum(1 for _, uid in self.access_records[model_name] if uid == user_id)

        # 检查是否超过限制
        if user_requests >= max_requests:
            return False

        # 记录本次访问
        self.access_records[model_name].append((current_time, user_id))

        # 更新用户统计
        self.user_stats[user_id][model_name] += 1

        return True

    def get_user_stats(self, user_id: str) -> Dict[str, int]:
        """
        获取用户的访问统计

        参数:
            user_id: 用户ID

        返回:
            dict: {model_name: count}
        """
        return dict(self.user_stats[user_id])

    def reset_user_stats(self, user_id: str):
        """
        重置用户的访问统计

        参数:
            user_id: 用户ID
        """
        if user_id in self.user_stats:
            del self.user_stats[user_id]

    def reset_model_records(self, model_name: str):
        """
        重置模型的访问记录

        参数:
            model_name: 模型名称
        """
        if model_name in self.access_records:
            del self.access_records[model_name]

    def rate_limit_decorator(self, model_name: str, user_id_getter: Callable[[], str]):
        """
        创建一个装饰器，用于限制函数的访问频率

        参数:
            model_name: 模型名称
            user_id_getter: 获取用户ID的函数

        返回:
            装饰器函数
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                user_id = user_id_getter()
                if not self.check_rate_limit(model_name, user_id):
                    raise Exception(f"Rate limit exceeded for model {model_name}")
                return func(*args, **kwargs)

            return wrapper

        return decorator


# 使用示例
if __name__ == "__main__":
    # 创建中间件实例
    middleware = RateLimitMiddleware()

    # 设置不同模型的访问限制
    middleware.set_rate_limit("gpt-4", max_requests=10, time_window=60)  # 每分钟最多10次
    middleware.set_rate_limit("gpt-3.5", max_requests=20, time_window=60)  # 每分钟最多20次


    # 模拟用户ID获取函数
    def get_user_id():
        return "user123"


    # 使用装饰器限制函数访问
    @middleware.rate_limit_decorator("gpt-4", get_user_id)
    def call_gpt4(prompt: str):
        return f"GPT-4 response to: {prompt}"


    # 测试访问限制
    for i in range(15):
        try:
            response = call_gpt4(f"Query {i + 1}")
            print(f"Request {i + 1}: Success - {response}")
        except Exception as e:
            print(f"Request {i + 1}: Failed - {str(e)}")

    # 获取用户统计
    print("\nUser stats:", middleware.get_user_stats("user123"))
