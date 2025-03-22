import redis

try:
    r = redis.Redis.from_url("redis://localhost")
    r.ping()
    print("Redis连接成功。")
except redis.exceptions.ConnectionError as e:
    print(f"无法连接到Redis: {e}")