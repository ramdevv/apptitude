# to impliment redis and make a cache for this
import redis.asyncio as redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend


async def init_redis_cache():

    # this line creats a redis client at is default port and it tells redis to treat all the values as a utf-8 string and also the response comes in the decodes way and not in the form of byte in which it was stored
    redis_client = redis.from_url(
        "redis://localhost:6379", encoding="utf8", decode_responses=True
    )

    # this line just initiates the global cache system which we will call from the main file
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
